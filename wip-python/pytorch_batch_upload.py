import torch
import torchvision.models as models
import torchvision.transforms as transforms
from torchvision.datasets import ImageFolder
from PIL import Image
import numpy as np
import sqlite3
import hashlib
import shutil
import os

import localstack_client.session
from botocore.exceptions import ClientError

# Setting logging
import logging
import datetime
logger = logging.getLogger(__name__)
formatter = logging.Formatter('[%(asctime)s] %(levelname)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
file_handler = logging.FileHandler('/data/similarity-search/training.log')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)
logger.setLevel((logging.INFO))

class S3Uploader:
  def __init__(self, bucket_name):
    self.endpoint_url = "http://localhost.localstack.cloud:4566"
    self.session = localstack_client.session.Session()
    self.client = self.session.client('s3')
    self.bucket_name = bucket_name
    self.__create_bucket_if_not_exists()
    
  def __create_bucket_if_not_exists(self):
    try:
      self.client.head_bucket(Bucket=self.bucket_name)
      logger.info(f"Bucket {self.bucket_name} exists")
    except ClientError as e:
      error_code = int(e.response['Error']['Code'])
      if error_code == 404:
          self.client.create_bucket(Bucket=self.bucket_name)
          logger.info(f"Bucket {self.bucket_name} created!")
      else:
          logger.info(f"Unexpected error when creating {self.bucket_name}: {e}")
          raise
  
  def upload_to_s3(self, source, target):
      try:
          self.client.upload_file(source, Bucket=self.bucket_name, Key=target)
          logger.info(f"Uploaded file from {source} to s3://{self.bucket_name}/{target}")
          raise
      except Exception as e:
          logger.error(f"Error uploading file from {source} to s3://{self.bucket_name}/{target}: {e}")
          raise

class SqliteDatabase:
  def __init__(self, db_path):
      try:
          self.conn = sqlite3.connect(db_path)
          self.cursor = self.conn.cursor()
          self.cursor.execute('''
          CREATE TABLE IF NOT EXISTS
            img_embeddings
            ( 
                file_raw_id INTEGER PRIMARY KEY AUTOINCREMENT, 
                file_id INTEGER AS (file_raw_id-1) VIRTUAL, 
                file_name TEXT, 
                embedding BLOB
            ) 
          '''
          )
          self.conn.commit()
      except sqlite3.Error as e:
          logger.error(f"Error connecting to SQLite database: {e}")
          raise
    
  def write_embedding(self, file_name, embedding):
      try:
          array_data = sqlite3.Binary(embedding.numpy().tobytes())
          self.cursor.execute('INSERT INTO img_embeddings(file_name, embedding) VALUES (?, ?)', (file_name, array_data))
          self.conn.commit()
          logger.info(f'Successfully wrote embedding for {file_name}')
      except Exception as e:
          logger.error(f'Error writing embedding for {file_name}: {str(e)}')
          self.conn.rollback()
          raise



def file_to_hash(file_path):
  """
  Compute the SHA-256 hash and file extension of a file.
  Args:
    file_path (str): The path to the file.

  Returns:
    str: A string containing the SHA-256 hash and file extension of the file.
  """
  with open(file_path, 'rb') as file:
      hash_object = hashlib.sha256()
      hash_object.update(file.read())
      file_hash = hash_object.hexdigest()
      
  file_name, file_extension = os.path.splitext(file_path)
  
  return file_hash + file_extension


# Load pre-trained ResNet-50 model
weights = models.ResNet50_Weights.IMAGENET1K_V2
resnet = models.resnet50(weights=weights)

# Define a custom loader that returns the filenames along with the images
class ImageFolderWithFilenames(ImageFolder):
    def __getitem__(self, index):
        filename = self.imgs[index][0]
        img = super().__getitem__(index)
        # img[0] contains the image data
        # img[1] contains label which can be discarded
        return img[0], filename

batch_size = 512
dataset = ImageFolderWithFilenames(root="/data/open-images-dataset/", transform=weights.transforms())
dataloader = torch.utils.data.DataLoader(dataset, batch_size=batch_size)

#s3_uploader = S3Uploader("pictures")
sqlite_db = SqliteDatabase("/data/similarity-search/embeddings.sqlite")
os.mkdir("/data/similarity-search/pictures")

for batch_idx, (data, file_names) in enumerate(dataloader):
  logger.info(f'Processing batch {batch_idx}/{len(dataloader)}')
  with torch.no_grad():
    embeddings = resnet(data)
    
  for file_name, embd in zip(file_names, embeddings):
    hash_file_name = file_to_hash(file_name)  
    sqlite_db.write_embedding(file_name=hash_file_name, embedding=embd)
    # In general, I would upload all the data to S3
    # s3_uploader.upload_to_s3(source=file_name, target=hash_file_name)
    shutil.copy(file_name, os.path.join("/data/similarity-search/pictures", hash_file_name))
  sqlite_db.conn.commit()


#df = pd.read_sql_query('SELECT file_id, file_name,  embedding FROM img_embeddings', sqlite_db.conn)
#df['embedding'] = df['embedding'].apply(lambda x: np.frombuffer(x, dtype=np.float32))
