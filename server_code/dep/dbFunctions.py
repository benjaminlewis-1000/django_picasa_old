#! /usr/bin/env python

# Database creation

import sqlite3
import xmltodict
import os
from photoLoader import photo
import warnings
import cv2 as cv
import numpy as np
import coloredlogs
import logging
import cnnFaceExtract

class database():

    def __init__(self, xmlParamFile):

        # Allow for colored logging outputs
        coloredlogs.install()

        # Read in the xml file that contains our parameters. 
        self.xmlParamFile = xmlParamFile
        with open(xmlParamFile) as stream:
            try:
                self.params = xmltodict.parse(stream.read())
                self.params = self.params['parameters']
            except Exception as exc:
                print(exc)
                exit(1)

        # Define the database file. It currently will reside in the same 
        # directory as the path to this script.
        db_file = self.params['databaseFile']
        db_file = os.path.join(path_to_script, db_file)

        # Set up a connection to the database. 
        self.conn = self.create_connection(db_file)

        # Read in table and column names for a variety of tables from the 
        # XML parameter file. These parameters will be used in populating
        # and creating the tables. We define them once here and then 
        # can use them anywhere in the class.

        photoTableParams = self.params['photoTable']
        self.photo_table_name = photoTableParams['name']
        self.photo_id_col = photoTableParams['id_col']
        self.photo_abs_path_column = photoTableParams['abs_path']
        self.orientationHashField = photoTableParams['orientationHash']
        self.photo_fully_processed = photoTableParams['fully_processed']

        chipTableParams = self.params['chipTable']
        self.chip_table_name = chipTableParams['name']
        self.chip_root_photo_col = chipTableParams['root_photo_col']
        self.face_linked_key = chipTableParams['face_linked_key']
        self.chip_path = chipTableParams['chip_path']
        self.chip_solved = chipTableParams['chip_solved']
        self.chip_centerX = chipTableParams['chip_centerX']
        self.chip_centerY = chipTableParams['chip_centerY']
        self.chip_width = chipTableParams['chip_width']
        self.chip_height = chipTableParams['chip_height']
        self.face_vector_column = chipTableParams['face_vector']
        self.potential_face_key_root = chipTableParams['potential_face_key_root']

        self.num_potential_chips = int(chipTableParams['num_potentials'])

        personTableParams = self.params['personNameTable']
        self.person_table_name = personTableParams['name']
        self.person_primary_key = personTableParams['personPrimaryKey']
        self.person_full_name_col = personTableParams['fullName']

        # Set up a dictionary that will hold the primary key values for each
        # person in the person table. The first time that a name is encountered,
        # we will add it to the dictionary; after that, this dictionary saves a 
        # query to the database every time that person is encountered.
        self.personKeys = dict()

    def new_database(self):

        # Create a table that will hold information about individual photos, including 
        # a primary key, the absolute path to the image, and a hash of the top-left 100x100 pixels
        # that we can use to determine if the orientation has changed. 
        photoTableSQL = '''CREATE TABLE IF NOT EXISTS {name} (\
            {id_col} integer PRIMARY KEY  AUTOINCREMENT,\
            {abs_path} text NOT NULL,\
            {orientation_hash_field} text,\
            {fully_processed} integer)'''.format(name=self.photo_table_name, id_col = self.photo_id_col, \
                abs_path = self.photo_abs_path_column, orientation_hash_field = self.orientationHashField, \
                fully_processed = self.photo_fully_processed)

        # Create a table that holds the names of all the people and their primary keys. 
        personTableSQL = '''CREATE TABLE IF NOT EXISTS {name} (
            {primary_key} integer PRIMARY KEY AUTOINCREMENT, \
            {person_name} text NOT NULL
            )'''.format(name = self.person_table_name, primary_key = self.person_primary_key, \
            person_name = self.person_full_name_col)

        # Create a subset of the SQL query that will be used to create the chip table.
        # These columns hold the top-n guesses that the NN has for what the identity of
        # a given unknown face is. 
        potential_col = ''
        for i in range(self.num_potential_chips):
            potential_row += '{potential_face}{num} int REFERENCES {person_table_name} ({person_primary_key}), \n'''\
                .format(potential_face = self.potential_face_key_root, 
                num = i + 1, person_table_name = self.person_table_name,
                person_primary_key = self.person_primary_key)

        # Create the table that holds information about every face chip, 
        # including references to the primary key of the photo it belongs to,
        # a reference to the truth value of the person it identifies (if known),
        # references to the primary keys of potential identities,
        # the path to the chip, whether it's been solved, and the positioning of the 
        # chip. It also holds a blob (may change) of a 128-dimensional vector 
        # describing the face. 
        chipTableSQL = '''CREATE TABLE IF NOT EXISTS {name} (
            {root_photo_col} integer REFERENCES {photo_table_name} ({photo_prim_key}), 
            {face_truth} int REFERENCES {person_table_name} ({person_primary_key}),
            {potential_fields}
            {chip_path} text NOT NULL,
            {chip_solved} int,
            {chip_centerX} int,
            {chip_centerY} int,
            {chip_width} int,
            {chip_height} int,
            {face_vector} blob
            )'''.format(name=self.chip_table_name, root_photo_col=self.chip_root_photo_col, \
            photo_table_name = self.photo_table_name, photo_prim_key = self.photo_id_col,\
            face_truth = self.face_linked_key, chip_path = self.chip_path, chip_centerX = self.chip_centerX,\
            chip_centerY = self.chip_centerY, chip_width = self.chip_width, chip_height = self.chip_height,\
            chip_solved = self.chip_solved, face_vector = self.face_vector_column,
            person_table_name = self.person_table_name, person_primary_key = self.person_primary_key,
            potential_fields = potential_col)

        self.clear_table(self.photo_table_name)
        self.clear_table(self.person_table_name)
        self.clear_table(self.chip_table_name)
        self.run_sql(photoTableSQL)
        self.run_sql(personTableSQL)
        self.run_sql(chipTableSQL)

        print chipTableSQL
        print photoTableSQL
        print personTableSQL

    def create_connection(self, db_file):
        """ create a database connection to a SQLite database """
        try:
            conn = sqlite3.connect(db_file)
            print(sqlite3.version)
            return conn
        except Error as e:
            print(e)

    def run_sql(self, desired_sql):
        """ create a table from the desired_sql statement
        :param conn: Connection object
        :param desired_sql: a CREATE TABLE statement
        :return:
        """
        try:
            c = self.conn.cursor()
            c.execute(desired_sql)
        except sqlite3.Error as e:
            print(e)
            print desired_sql
            raise(e)

        self.conn.commit()

    def clear_table(self, tableName):
        try:
            c = self.conn.cursor()
            dropTable = 'DROP TABLE IF EXISTS ' + tableName

            c.execute(dropTable)
        except sqlite3.Error as e:
            print(e)

        self.conn.commit()

    def processPhoto(self, imagePath):

        photoObj = photo(imagePath, self.xmlParamFile)
        photos_faces = photoObj.extract_stored_faces()

        photoWidth = photoObj.photoWidth
        photoHeight = photoObj.photoHeight
        photoPathHash = photoObj.pathHash
        orientationHash = photoObj.orientationHash

        # Sequentially number the faces 
        faceNum = 0

        photo_primary_key = self.addFullPhotoToDB(imagePath, orientationHash)
        photoObj.primaryKey = photo_primary_key
        print "Primary key for photo is:" + str(photo_primary_key)
        logging.warn('Random face vector implemented - actual face vector implementation todo')

        for eachFace in photos_faces:

            personName = eachFace['name']
            face_rectangle = eachFace['rectangle']
            # roi = eachFace['chip_image']

            faceNum, faceDBStruct = cnnFaceExtract.processChip(face_rectangle, photoObj, faceNum, self.params)
            print faceNum
            faceDBStruct['assigned_name'] = personName

            self.addChipToDB(faceDBStruct)

        cnn_faces = cnnFaceExtract.imageFaceDetect(photoObj, faceNum, self.params)

        for detectedFace in cnn_faces:
            face_vector = detectedFace['face_vector']
            best_guesses = cnnFaceExtract.classifyFaces(face_vector)
            detectedFace['best_guesses'] = best_guesses

            self.addChipToDB(detectedFace)


    def addFullPhotoToDB(self, photoPath, orientationHash):
        getID = '''SELECT {id_col}, {orientation_hash_field} FROM {photo_table_name} WHERE {abs_path} = "{photo_path}";'''\
            .format(photo_table_name=self.photo_table_name, abs_path = self.photo_abs_path_column, \
            photo_path = photoPath, id_col = self.photo_id_col, \
            orientation_hash_field = self.orientationHashField)

        c = self.conn.cursor()
        c.execute(getID)
        values = c.fetchall()
        if len(values) != 0:
            id_num = values[0][0]
            storedHash = values[0][1]
        else:
            id_num = None
            storedHash = None

        # Cases:
        # 1: We've never seen this photo before ( id_num is None )
        # 2: Seen photo but orientation is the same ( id_num is not None and orientationHash == storedHash )
        # 3: Seen photo but orientation is different ( id_num is not None and orientationHash != storedHash )

        # For all three cases, this first SQL statement will work. We will just have to update the orientation
        # hash for case #3. 
        SQL = \
        '''INSERT INTO {photo_table_name} ({abs_path}, {fully_processed}, {orientation_hash_field}) \
            SELECT "{photo_path}", "0", "{passed_orientation_hash}" \
            WHERE NOT EXISTS(SELECT 1 FROM {photo_table_name} WHERE {abs_path} = "{photo_path}");''' \
        .format(photo_table_name=self.photo_table_name, abs_path = self.photo_abs_path_column, \
            fully_processed = self.photo_fully_processed, photo_path = photoPath,
            passed_orientation_hash = orientationHash, orientation_hash_field = self.orientationHashField)

        self.run_sql(SQL)

        if (id_num is not None) and (storedHash != orientationHash):
            print "Rotated image found. Updating hash."
            update_orient_hash = ''' UPDATE {photo_table_name} \
                SET {orientation_hash_field} = "{passed_orientation_hash}" \
                WHERE {abs_path} = "{photo_path}";'''.format( \
                photo_table_name=self.photo_table_name, abs_path = self.photo_abs_path_column, \
                photo_path = photoPath, passed_orientation_hash = orientationHash, \
                orientation_hash_field = self.orientationHashField)

            self.run_sql(update_orient_hash)


        if id_num is None:
            c = self.conn.cursor()
            c.execute(getID)
            id_num = c.fetchall()[0][0]
        
        return id_num

    def addChipToDB(self, faceDBStruct):

        photo_primary_key     =   faceDBStruct['photo_primary_key']
        center_X        =   faceDBStruct['center_X_scaled']
        center_Y        =   faceDBStruct['center_Y_scaled']
        width_scale     =   faceDBStruct['width_scale']
        height_scale    =   faceDBStruct['height_scale']
        chip_save_name  =   faceDBStruct['chip_save_name']
        face_vector     =   faceDBStruct['face_vector']
        assigned_name   =   faceDBStruct['assigned_name']
        best_guesses    =   faceDBStruct['best_guesses']

        if best_guesses is not None:
            assert len(best_guesses) == 5, 'Best guesses should be of length 5 or None.'
        assert (best_guesses is None) is not (assigned_name is None), \
            'Either a name should be assigned or five guesses should be assigned.'
        # Best guesses should be linked instead of hard-entry 
        pass

        def getNamePrimaryKey(name):
            if name in self.personKeys:
                primary_key = self.personKeys[name]
            else:
                getPersonPrimaryKeySQL = '''SELECT {primary_key} FROM {person_name_table} \
                    WHERE {person_full_name_col} = "{name}"'''\
                    .format(primary_key = self.person_primary_key,\
                    person_name_table = self.person_table_name, \
                    person_full_name_col = self.person_full_name_col, name=name)
    
                # Check to see if the person is in the table...  
                c = self.conn.cursor()
                c.execute(getPersonPrimaryKeySQL)
                values = c.fetchall()
                if len(values) != 0:
                    primary_key = values[0][0]
                else:
                    primary_key = None

                    # Insert into the table... 

                    addPersonSQL = '''INSERT INTO {person_name_table} ( {person_full_name_col} ) \
                        VALUES ("{name}"); '''.format(person_name_table = self.person_table_name, \
                        person_full_name_col = self.person_full_name_col, name=name)

                    # print addPersonSQL
                    self.run_sql(addPersonSQL)

                    c.execute(getPersonPrimaryKeySQL)
                    primary_key = c.fetchall()[0][0]

                # Add the primary key to the dictionary
                self.personKeys[name] = primary_key

        if assigned_name is not None:
            getNamePrimaryKey(assigned_name)
        else:
            for i in range(len(best_guesses)):
                getNamePrimaryKey(best_guesses[i])

 
if __name__ == '__main__':


    path_to_script = os.path.dirname(os.path.realpath(__file__))
    xmlParamFile = os.path.join(path_to_script, 'params.xml')

    dbObj = database(xmlParamFile)

    from shutil import copyfile

    testFile = '/tmp/copyfile.jpg'
    copyfile('/home/lewis/test_imgs/DSC_9833.JPG', testFile )
    dbObj.new_database()

    dbObj.processPhoto(testFile)
    os.system('/usr/bin/exiftran ' + testFile + " -i9")
    dbObj.processPhoto(testFile)
    dbObj.processPhoto(testFile)


