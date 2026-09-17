import asyncio
import json
import socket
import subprocess
import urllib.request

import av
from libdatachannel import H264RtpDepacketizer, NalUnit, RtcpReceivingSession
from teleoprtc import StreamingOffer, WebRTCOfferBuilder
from teleoprtc.stream import RTCSessionDescription

class Connection:
  def __init__(self, host):
    self.host = host
    self.tunnel = None
    self.port = None

  async def __call__(self, offer: StreamingOffer):
    if self.tunnel is None:
      with socket.socket() as sock:
        sock.bind(('127.0.0.1', 0))
        self.port = sock.getsockname()[1]
      self.tunnel = await asyncio.create_subprocess_exec(
        'ssh', '-T', '-o', 'BatchMode=yes', '-o', 'ConnectTimeout=5', '-o', 'LogLevel=ERROR',
        '-o', 'StrictHostKeyChecking=no', '-o', 'UserKnownHostsFile=/dev/null', '-o', 'GlobalKnownHostsFile=/dev/null',
        '-o', 'ConnectionAttempts=1', '-o', 'ForkAfterAuthentication=no', '-o', 'ExitOnForwardFailure=yes', '-L',
        f'127.0.0.1:{self.port}:127.0.0.1:5001', f'comma@{self.host}',
        'cd /data/openpilot && /usr/local/venv/bin/python -c '
        "'from openpilot.common.params import Params; from openpilot.system.webrtc.helpers import wait_for_webrtcd; "
        "Params().put_bool(\"IsLiveStreaming\", True); wait_for_webrtcd()' && echo READY && exec cat",
        stdin=asyncio.subprocess.PIPE, stdout=asyncio.subprocess.PIPE)
      async with asyncio.timeout(11):
        while await self.tunnel.stdout.readline() != b'READY\n':
          if self.tunnel.stdout.at_eof(): raise subprocess.CalledProcessError(await self.tunnel.wait() or 1, 'ssh')
    body = json.dumps({'sdp': offer.sdp, 'cameras': [offer.video[0]], 'enabled': True}).encode()
    request = urllib.request.Request(f'http://127.0.0.1:{self.port}/stream', body,
                                     {'Content-Type': 'application/json'})
    with urllib.request.urlopen(request, timeout=10) as response:
      answer = json.load(response)
    return RTCSessionDescription(answer['sdp'], answer['type'])

  async def close(self):
    if self.tunnel and self.tunnel.returncode is None:
      self.tunnel.kill()
      await asyncio.wait_for(self.tunnel.wait(), 1)


class Receiver:
  def __init__(self, track):
    self.loop = asyncio.get_running_loop()
    self.queue = asyncio.Queue(2)
    self.decoder = av.CodecContext.create('h264', 'r')
    self.depacketizer = H264RtpDepacketizer(NalUnit.Separator.StartSequence)
    self.rtcp = RtcpReceivingSession()
    track.set_media_handler(self.depacketizer)
    track.chain_media_handler(self.rtcp)
    track.on_frame(lambda data, _: self.loop.call_soon_threadsafe(self.enqueue, bytes(data)))
    self.track = track
    track.request_keyframe()

  def enqueue(self, data):
    if self.queue.full(): self.queue.get_nowait()
    self.queue.put_nowait(data)

  async def recv(self):
    while True:
      try:
        for packet in self.decoder.parse(await self.queue.get()):
          frames = self.decoder.decode(packet)
          if frames: return frames[-1].to_ndarray(format='bgr24')
      except av.FFmpegError:
        self.track.request_keyframe()

  def close(self):
    self.track.reset_callbacks()
    self.track.close()
    self.track = self.depacketizer = self.rtcp = None


async def frames(host, camera):
  connection = Connection(host)
  builder = WebRTCOfferBuilder(connection)
  builder.offer_to_receive_video_stream(camera)
  stream = builder.stream()
  receiver = None
  try:
    await asyncio.wait_for(stream.start(), 12)
    await asyncio.wait_for(stream.wait_for_connection(), 10)
    receiver = Receiver(stream.get_incoming_video_track(camera))
    while stream.is_connected_and_ready:
      try:
        yield await asyncio.wait_for(receiver.recv(), 0.5)
      except TimeoutError:
        receiver.track.request_keyframe()
  finally:
    if receiver: receiver.close()
    await stream.stop()
    await connection.close()
