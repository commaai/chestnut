import asyncio
import json
import urllib.request

import av
from libdatachannel import H264RtpDepacketizer, NalUnit, RtcpReceivingSession
from teleoprtc import StreamingOffer, WebRTCOfferBuilder
from teleoprtc.stream import RTCSessionDescription

class Connection:
  def __init__(self, host):
    self.url = f'http://{host}:5001/stream'

  async def __call__(self, offer: StreamingOffer):
    return await asyncio.to_thread(self.connect, offer)

  def connect(self, offer):
    body = json.dumps({'sdp': offer.sdp, 'cameras': offer.video, 'enabled': True,
                       'bridge_services_in': [], 'bridge_services_out': []}).encode()
    request = urllib.request.Request(self.url, body, {'Content-Type': 'application/json'})
    with urllib.request.urlopen(request, timeout=10) as response:
      answer = json.load(response)
    return RTCSessionDescription(answer['sdp'], answer['type'])


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
  tunnel = await asyncio.create_subprocess_exec('ssh', '-N', '-L', '5001:localhost:5001', f'comma@{host}')
  await asyncio.sleep(0.5)
  builder = WebRTCOfferBuilder(Connection('localhost'))
  builder.offer_to_receive_video_stream(camera)
  stream = builder.stream()
  await stream.start()
  await stream.wait_for_connection()
  receiver = Receiver(stream.get_incoming_video_track(camera))
  try:
    while stream.is_connected_and_ready:
      try:
        yield await asyncio.wait_for(receiver.recv(), 0.5)
      except TimeoutError:
        receiver.track.request_keyframe()
  finally:
    receiver.close()
    await stream.stop()
    tunnel.terminate()
    await tunnel.wait()
