'''
'''
import os 
import h5py
import numpy as np 


dat_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'dat')


class Calories(object): 
    def __init__(self, source='loseit'):  
        self.source = source 
        self.data = None 

    def daily(self): 
        ''' compile daily values and remove incomplete days
        '''
        if self.data is None: 
            self.read() 
    
        dailys = {'date': [], 'meal': [], 'exercise': []} 

        for date in np.unique(np.sort(self.data['date'])): 
            sameday = (self.data['date'] == date) 

            types = list(np.unique(self.data['type'][sameday])) 

            # I never miss lunch or dinner so if they're missing this is an incomplete day 
            if not np.all([meal in types for meal in ['Lunch', 'Dinner']]): 
                continue 
            
            # add up exercise 
            exercise = 0. 
            if 'Exercise' in types: 
                exercise += np.sum(self.data['calories'][sameday &
                    (self.data['type'] == 'Exercise')])
                types.remove('Exercise') 

            # add up all the meals 
            meals = 0. 
            for _type in types: 
                istype = (self.data['type'] == _type) 
                meals += np.sum(self.data['calories'][sameday & istype]) 

            dailys['date'].append(date)
            dailys['meal'].append(meals)
            dailys['exercise'].append(exercise)

        for k in dailys.keys(): 
            dailys[k] = np.array(dailys[k]) 

        return dailys 
    
    def read(self): 
        ''' read data 
        '''
        fhdf5 = os.path.join(dat_dir, '%s.hdf5' % self.source)

        if not os.path.isfile(fhdf5): 
            # preprocess the data 
            self.preproc() 
        
        h5 = h5py.File(fhdf5, 'r') 

        self.data = {}
        for col in h5.keys(): 
            self.data[col.lower()] = h5[col][...]
        h5.close() 
        return self.data 

    def preproc(self): 
        ''' proprocess data 
        '''
        if self.source != 'loseit': raise NotImplementedError  
        
        import glob 
        import pandas as pd

        fweeks = glob.glob(os.path.join(dat_dir, 'WeeklySummary*.csv')) 
        
        for i, fweek in enumerate(fweeks): 
            week = pd.read_csv(fweek) 
            if i == 0: 
                cols = week.columns
                data = [np.array(week[col]) for col in cols] 
            else: 
                assert np.array_equal(np.array(week.columns), np.array(cols))

                for i in range(len(week.columns)): 
                    data[i] = np.concatenate([data[i], week[cols[i]]])
        
        # save to hdf5  
        h5 = h5py.File(os.path.join(dat_dir, '%s.hdf5' % self.source), 'w') 
        # no meta data for now 
        for i, col in enumerate(cols): 
            if isinstance(data[i][0], str):  
                h5.create_dataset(col, data=data[i], dtype=h5py.string_dtype()) 
            else: 
                h5.create_dataset(col, data=data[i]) 
        h5.close() 
        return None 
