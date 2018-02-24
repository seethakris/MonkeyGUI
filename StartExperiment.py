import os
import cv2
import pandas as pd
import csv
import numpy as np
from psychopy import core
import sys
from copy import copy


class Experiment(object):
    def __init__(self, NumberOfTrials, RewardTimeOut, Map, RewardLocationCSV, ExperimentParamFolder):
        """ Initialise user input
                Params :
                NumberOfTrials : number of trials in experiment
                RewardTimeout : number of seconds after which the trial ends and no reward is given
                Map : map of the area stored as .pgm
                RewardLocationCSV : csv file that contains reward locations
                ExperimentParamFolder : folder to save experiment related parameters

        """
        self.ExperimentParamFolder = ExperimentParamFolder
        cv2.namedWindow('CheckRewardLocation', cv2.WINDOW_NORMAL)
        self.map = cv2.imread(Map)
        print(np.shape(self.map))
        self.rewardlocation = pd.read_csv(RewardLocationCSV, index_col=0)
        print 'Number of saved reward locations loaded : ', len(self.rewardlocation)
        self.plot_saved_location()

        # Initialise Trial parameters
        self.numtrials = NumberOfTrials
        self.rewardtimeout = RewardTimeOut
        self._currenttrial = 0  # Trial number
        self.start_experiment()

    def plot_saved_location(self):
        """ Check if the saved reward locations are correct"""
        locationmap = copy(self.map)
        for index, row in self.rewardlocation.iterrows():
            cv2.circle(locationmap, (row['x'], row['y']), 20, (0, 0, 255), -1)
            cv2.putText(locationmap, '(%d, %d)' % (row['x'], row['y']), (row['x'], row['y']), cv2.FONT_HERSHEY_SIMPLEX,
                        2, (0, 0, 0), 4, cv2.LINE_AA)
        print('Press Esc if reward locations are correct')
        while True:
            cv2.imshow('CheckRewardLocation', locationmap)
            if cv2.waitKey(20) & 0xFF == 27:
                break
        cv2.imwrite(os.path.join(self.ExperimentParamFolder, 'RewardLocationsused.tif'), locationmap)
        cv2.destroyAllWindows()

    def updatetrial(self):
        """ Update trial """
        self._currenttrial += 1

    def start_experiment(self):
        """ Display a reward location and start timer"""
        while self._currenttrial < self.numtrials:
            print ('Trial %d beginning...' % self._currenttrial)
            currentreward = np.random.choice(len(self.rewardlocation), 1)
            currentrewardlocation = self.rewardlocation.iloc[currentreward]

            # Start trial - show reward
            print ('Go to reward location (%d, %d)' % (currentrewardlocation['x'], currentrewardlocation['y']))
            self.plotrewardlocation(currentrewardlocation)

            # Set up plot for realtime plotting
            cv2.namedWindow('Trial %d Reward' % self._currenttrial, cv2.WINDOW_NORMAL)
            cv2.resizeWindow('Trial %d Reward' % self._currenttrial, 600, 600)

            # Get initial location of robot
            loc_x, loc_y = self.get_random_xy_loc(currentrewardlocation)

            # Start timer for reward timeout
            timer = core.CountdownTimer(self.rewardtimeout)
            abstime = core.MonotonicClock()

            while timer.getTime() > 0:
                # Print elapsed time on map and console
                # Change location for testing purposes
                loc_x += 1
                loc_y += 1
                elapsedtime = abstime.getTime()
                self.realtime_elapsedtime(rewardloc=currentrewardlocation,
                                          elapsedtime=elapsedtime, robotloc=(loc_x, loc_y))
                print "\033[K Elapsed Time : ", elapsedtime, "\r",
                sys.stdout.flush()

            print('\n Trial Ended')
            cv2.destroyAllWindows()
            self.updatetrial()  # Trial ended - start of next trial

    def realtime_elapsedtime(self, rewardloc, elapsedtime, robotloc):
        """ Plot elapsed time, current robot location and reward location. Plot every refresh rate """
        locationmap = copy(self.map)
        cv2.circle(locationmap, (rewardloc['x'], rewardloc['y']), 50, (0, 0, 255), 20)
        cv2.putText(locationmap, 'Time : %0.4f' % elapsedtime, (20, 200), cv2.FONT_HERSHEY_SIMPLEX,
                    4, (0, 0, 0), 6, cv2.LINE_AA)
        cv2.putText(locationmap, '*', robotloc, cv2.FONT_HERSHEY_SIMPLEX,
                    5, (0, 0, 255), 6, cv2.LINE_AA)
        cv2.imshow('Trial %d Reward' % self._currenttrial, locationmap)

        # waitKey(Delay) in milliseconds
        # HighGui functions like imshow() need a call of waitKey, in order to process its event loop.
        # Plotting will be at refresh rate. Will not affect timing
        cv2.waitKey(1)

    def plotrewardlocation(self, rewardloc):
        """ Plot the reward location on the Map"""
        locationmap = copy(self.map)
        cv2.namedWindow('Trial %d Reward' % self._currenttrial, cv2.WINDOW_NORMAL)
        cv2.circle(locationmap, (rewardloc['x'], rewardloc['y']), 50, (0, 0, 255), 20)
        cv2.imshow('Trial %d Reward' % self._currenttrial, locationmap)
        cv2.waitKey(2000)  # Show plot for 5 seconds
        cv2.destroyAllWindows()

    def get_random_xy_loc(self, rewardloc):
        """ For testing : Randomly generate an x and y position for the robot
        that is around the chosen reward"""
        x = np.random.randint(rewardloc['x'] - 200, rewardloc['x'] + 200)
        y = np.random.randint(rewardloc['y'] - 200, rewardloc['y'] + 200)

        return x, y


def SaveExpParameters(ExperimentParamFolder, **kwargs):
    with open(os.path.join(ExperimentParamFolder, 'ExperimentParameters.csv'), 'wb') as f:  # Just use 'w' mode in 3.x
        w = csv.writer(f)
        for key, value in kwargs.items():
            w.writerow([key, value])


if __name__ == '__main__':
    LocationMap = '/Users/seetha/Desktop/MonkeyRewardTask/SampleData/map1.pgm'
    RewardLocationCSV = '/Users/seetha/Desktop/MonkeyRewardTask/SampleData/rewardlocations.csv'

    # Define Experiment Parameters here
    ExperimentNumber = 1
    ExperimentDate = '21022018'
    MonkeyName = 'Chimpian'
    NumberOfTrials = 10
    RewardTimeOut = 10  # In seconds
    ExperimentFolder = '/Users/seetha/Desktop/MonkeyRewardTask/SampleData/'  # Main folder for saving related data

    # Create a folder to save Experiment related parameters
    SaveDataFolder = os.path.join(ExperimentFolder, ExperimentDate, str(ExperimentNumber) + '_' + MonkeyName)
    if not os.path.exists(SaveDataFolder):
        os.makedirs(SaveDataFolder)

    # Save Experiment parameters
    SaveExpParameters(SaveDataFolder,
                      ExperimentNumber=ExperimentNumber,
                      ExperimentDate=ExperimentDate,
                      MonkeyName=MonkeyName,
                      NumberOfTrials=NumberOfTrials,
                      RewardTimeOut=RewardTimeOut)

    # Start Experiment
    Experiment(NumberOfTrials=10,
               RewardTimeOut=10,
               Map=LocationMap,
               RewardLocationCSV=RewardLocationCSV,
               ExperimentParamFolder=SaveDataFolder)
