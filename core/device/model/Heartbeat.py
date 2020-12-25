import json
from time import time

import paho.mqtt.client as mqtt

from core.base.model.ProjectAliceObject import ProjectAliceObject
from core.commons import constants
from core.device.model.Device import Device


class Heartbeat(ProjectAliceObject):

	def __init__(self, device: Device, tempo: int = 0, topic: str = constants.TOPIC_CORE_HEARTBEAT):
		super().__init__()
		self._client = None

		if tempo == 0:
			self._tempo = device.deviceType.heartbeatRate
		else:
			self._tempo = tempo

		self._topic = topic
		self._rnd = 0
		self._device = device
		self.startHeartbeat()


	def startHeartbeat(self):
		self._rnd = int(time())
		self.ThreadManager.newThread(name=f'heartBeatThread-{self._rnd}', target=self.thread)


	def stopHeartBeat(self):
		self.ThreadManager.terminateThread(name=f'heartBeatThread-{self._rnd}')


	def thread(self):
		self._client = mqtt.Client()

		if self.ConfigManager.getAliceConfigByName('mqttUser') and self.ConfigManager.getAliceConfigByName('mqttPassword'):
			self._client.username_pw_set(self.ConfigManager.getAliceConfigByName('mqttUser'), self.ConfigManager.getAliceConfigByName('mqttPassword'))

		if self.ConfigManager.getAliceConfigByName('mqttTLSFile'):
			self._client.tls_set(certfile=self.ConfigManager.getAliceConfigByName('mqttTLSFile'))
			self._client.tls_insecure_set(False)

		self._client.connect(self.ConfigManager.getAliceConfigByName('mqttHost'), int(self.ConfigManager.getAliceConfigByName('mqttPort')))
		self._client.loop_start()
		self.beat()


	def beat(self):
		if not self.ProjectAlice.shuttingDown:
			self._client.publish(topic=self._topic, payload=json.dumps({'uid': self._device.uid}), qos=0, retain=False)
		self.ThreadManager.newTimer(interval=self._tempo, func=self.beat)
