from melo.api import TTS

model = TTS(language='JP', device='cpu')
speaker_ids = model.hps.data.spk2id

print(speaker_ids)