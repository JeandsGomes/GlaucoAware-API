import pymongo

class SGBD():
    def __init__(self):
        connection_url = '' # MongoDB connection URL
        raise Exception('Please, set the connection URL to your MongoDB database in the mongo_db.py file. \n')
        self.client = pymongo.MongoClient(connection_url)
        database_name = "GlaucoAware"
        self._DataBase = self.client[database_name]
        
        mng_colection_name = "Manager"
        self._mng_colection = self._DataBase[mng_colection_name]

        identity_colction_name = "Metadata_Images"
        self._identity_colection = self._DataBase[identity_colction_name]

        self.mngs = {}

    @property
    def DataBase(self):
        return self._DataBase
    
    @DataBase.setter
    def DataBase(self,new_DataBase):
        self._DataBase = new_DataBase
        
    @property
    def mng_colection(self):
        return self._mng_colection
    
    @mng_colection.setter
    def mng_colection(self,new_mng_colection):
        self._mng_colection = new_mng_colection

    @property
    def metadata_images(self):
        return self._metadata_images

    @metadata_images.setter
    def metadata_images(self,new_metadata_images):
        self._metadata_images = new_metadata_images


    def close_bd(self):
        self.client.close()