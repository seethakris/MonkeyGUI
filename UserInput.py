import cv2
import os
import pandas as pd
import numpy as np


class MarkRewardLocations(object):
    def __init__(self, Map, RewardLocationFolder):
        """ Displays map of the location and takes double click from the user to mark reward location
                Params:
                Map : map of the area stored as .pgm
                RewardLocationFolder : Folder to save csv file and reward location image
        """
        self.rewardlocfolder = RewardLocationFolder

        # Get reward locations
        cv2.namedWindow('LocationMap', cv2.WINDOW_NORMAL)
        self.map = cv2.imread(Map)
        print('Map coordinates ', np.shape(self.map)[0:2])
        self.rewardlocation = {'x': [], 'y': []}
        cv2.setMouseCallback('LocationMap', self.mark_location_and_store)
        self.plot_location()
        self.save_reward_location()

    def mark_location_and_store(self, event, x, y, flags, param):
        """ Double click on the location map to get x, y coordinates for reward location"""
        if event == cv2.EVENT_LBUTTONDBLCLK:
            cv2.circle(self.map, (x, y), 20, (0, 0, 255), -1)
            cv2.putText(self.map, '(%d, %d)' % (x, y), (x, y), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 0), 4,
                        cv2.LINE_AA)
            self.rewardlocation['x'].append(x)
            self.rewardlocation['y'].append(y)

    def plot_location(self):
        """ Plot image with reward location. Press esc to quit"""
        print('Press Esc when done marking locations')
        while True:
            cv2.imshow('LocationMap', self.map)
            if cv2.waitKey(20) & 0xFF == 27:
                break
        cv2.destroyAllWindows()

    def save_reward_location(self):
        print 'Saving reward locations'
        df = pd.DataFrame.from_dict(self.rewardlocation)
        df.to_csv(os.path.join(self.rewardlocfolder, 'rewardlocations.csv'))
        cv2.imwrite(os.path.join(self.rewardlocfolder, "rewardlocations.tif"), self.map)


if __name__ == '__main__':
    LocationMap = '/Users/seetha/Desktop/MonkeyRewardTask/SampleData/map1.pgm'
    RewardLocationFolder = '/Users/seetha/Desktop/MonkeyRewardTask/SampleData/'

    MarkRewardLocations(Map=LocationMap,
                        RewardLocationFolder=RewardLocationFolder)
