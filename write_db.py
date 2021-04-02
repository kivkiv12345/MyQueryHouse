"""
Helper class to write database filler data to a .json file.
"""
if __name__ == '__main__':
    from json import dump
    from utils import DB_DATA_FILE

    db_dict = {  # Filler data goes here:
        'Location (shelf, space)':
            ((3,5), (3,6), (6,8), (9,3), (8,3)),
        'Item (productname, description)':
            (('testproduct1', 'does some tests and stuff'), ('alsotestproduct', 'amazing')),
    }

    with open(DB_DATA_FILE, 'w') as json_file:
        dump(db_dict, json_file, indent=4)
else:
    print("Ignored an attempt to run write_db.py outside of __main__")