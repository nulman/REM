

class test(object):
    def getparameters(self):
        #return {'Line': {'x-axis':'single', 'y-axis':'single', 'group-by':'multiple'}}
        params = {}
        params['x_axis'] = {'type':'single','source':'cols'}
        params['y_axis'] = {'type':'single','source':'cols'}
        params['group_by'] ={'type':'multiple','source':'machines'}
        return {'test':params}