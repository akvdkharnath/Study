import  boto3


class S3(object):

    def __init__(self):
        self.conn = boto3.client('s3')
    
    def create_bucket(self, name:str):
        self.conn.create_bucket(Bucket=name)

    def get_list(self):
        data = self.conn.list_buckets()
        print(data)




S3Operations =S3()

# create bucket

# name = "h22"
# S3Operations.create_bucket(name)

S3Operations.get_list()
