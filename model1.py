from hecuba import StorageObj



class ModelData(StorageObj):
    '''
    @ClassField nilev int
    @ClassField nfields int
    @ClassField data dict <<ts:double>, fields_data:numpy.ndarray>
    '''
    pass


class Experiment(StorageObj):
    """
    @ClassField id str
    @ClassField time_resolution int
    @ClassField nlats int
    @ClassField nlons int
    @ClassField grid dict <<lat:double>, nlons:int, total_index:int>
    @ClassField Data model1.ModelData
    """

