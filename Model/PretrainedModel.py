import base64
import re
from io import BytesIO

import torch
import sys
from .nnmodel import EncoderCNN,DecoderRNN#,Vocabulary
from PIL import Image
import pickle 
from torchvision import transforms
from googletrans import Translator

# Device configuration
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

with open('./Model/models/vocab.pkl', 'rb') as f:
    vocab = pickle.load(f)

def base64_to_image(base64_str, image_path=None):
    base64_data = re.sub('^data:image/.+;base64,', '', base64_str)
    byte_data = base64.b64decode(base64_data)
    image_data = BytesIO(byte_data)
    img = Image.open(image_data).convert('RGB')
    return img

def load_image(image_path, transform=None):
    if re.match('^data:image/.+;base64,',image_path):
        image = base64_to_image(image_path)
    else:
        image = Image.open(image_path)
    image = image.resize([224, 224], Image.LANCZOS)
    if transform is not None:
        image = transform(image).unsqueeze(0)
    return image

class img2words(object):
    def __init__(self):
        self.embed_size = 256
        self.hidden_size = 512
        self.num_layers = 1
        self.vocab_path = './Model/models/vocab.pkl'
        self.encoder_path = './Model/models/encoder-5-3000.pkl'
        self.decoder_path = './Model/models/decoder-5-3000.pkl'
        self.transform = transforms.Compose([
                transforms.ToTensor(), 
                transforms.Normalize((0.485, 0.456, 0.406), 
                                     (0.229, 0.224, 0.225))])
        self.vocab = vocab

        self.encoder = EncoderCNN(self.embed_size).eval()  # eval mode (batchnorm uses moving mean/variance)
        self.decoder = DecoderRNN(self.embed_size,self.hidden_size, len(self.vocab), self.num_layers)
        self.encoder = self.encoder.to(device)
        self.decoder = self.decoder.to(device)

        self.encoder.load_state_dict(torch.load(self.encoder_path))
        self.decoder.load_state_dict(torch.load(self.decoder_path))

    def get_sentence(self,image):
        image = load_image(image, self.transform)
        image_tensor = image.to(device)

        feature = self.encoder(image_tensor)
        sampled_ids = self.decoder.sample(feature)
        sampled_ids = sampled_ids[0].cpu().numpy()          # (1, max_seq_length) -> (max_seq_length)


        sampled_caption = []
        for word_id in sampled_ids:
            word = self.vocab.idx2word[word_id]
            sampled_caption.append(word)
            if word == '<end>':
                break
        sentence = ' '.join(sampled_caption)
        translator = Translator(service_urls=['translate.google.cn'])
        sentence_ch = translator.translate(sentence[7:len(sentence)-5],src='en',dest='zh-cn').text
        return sentence[7:len(sentence)-5],sentence_ch

if __name__ == '__main__':
    m = img2words()
    image = r'.\Model\img\wallhaven-630501.jpg'
    print(m.get_sentence(image))




