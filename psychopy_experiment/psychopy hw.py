#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: nickhoang
"""
import numpy as np
import pandas as pd
import os, sys
from psychopy import visual, core, event, gui, logging

#%%% use built-in gui to collect session information

# create a gui object
subgui = gui.Dlg()

# add fields. the strings become the labels in the gui
subgui.addField("Subject ID:")
subgui.addField("Session Number:")

# show the gui
subgui.show()

# put the inputted data in easy to use variables
subjID = subgui.data[0]
sessNum = subgui.data[1]

#%%% set output file name and check if we have the same subject already
ouputFileName = 'output_data' + os.sep + 'sub' + subjID + '_sess' + sessNum + '.csv'
if os.path.isfile(ouputFileName) :
    sys.exit("data for this session already exists")

#%% set output dataframe name for output recording
outVars = ['subj', 'sess', 'scene', 'trial', 'stimOn', 'questOn', 'response', 'rt', ]    
out = pd.DataFrame(columns=outVars)

# open a white full screen window
win = visual.Window(fullscr=True, allowGUI=False, color='black', unit='height') # set unit as 'height' to make positions easy to understand


#%% prepare stimuli needed later in the trial
# prepare instruction
instr = visual.ImageStim(win, image="instruction.png", size= 1, interpolate=True)
question = visual.ImageStim(win, image="question.png", size= 1, interpolate=True)

# prepares fixation in the middle
fixation = visual.TextStim(win, text='+', height=.1, color='white', bold=True, pos=(0,0))

# read in trial info
trialInfo = pd.read_excel('sceneCond.xlsx')  # this xlsx file should be in the same directory as the code file and scene pictures

# randomize trials
# the sample method lets you randomly sample (without replacement) from a 
# dataframe. frac determines the fraction of trials sampled 
trialInfo = trialInfo.sample(frac=1)
trialInfo = trialInfo.reset_index()

# set stimulus times in seconds
isiDur = 0.5
sceneDur = 3
questDur = 3

# set number of trials
nTrials = len(trialInfo)


#%%%% experiment start

# draw and show instruction
instr.draw()
event.clearEvents() # this clears any prior button presses
win.flip()

event.waitKeys(keyList = ["space"])  # wait for button press "space" to move on

# set global quitting
if event.getKeys(['esc']):
    win.close()
    core.quit()


# trial loop
expClock = core.Clock() # won't reset
trialClock = core.Clock() # will reset at the beginning of each trial
stimClock = core.Clock() # will reset when stim are presented
questClock = core.Clock() # will reset when question are presented
for thisTrial in np.arange(0,nTrials):
    
    trialClock.reset()
    
    event.clearEvents()  # clear all key presses before this trial
    
    # draw a fixation cross
    fixation.draw()
    win.flip()
    
    # prepare stimuli during fixation period
    thisScene = visual.ImageStim(win, image=trialInfo.loc[thisTrial,'scenes'],   # read in the trialInfo for the column scenes in the xlsx file
                                size= 1, pos=(0,0),interpolate=True)   
    thisScene.draw()
    
    # record trial prarameters
    out.loc[thisTrial,'scene'] = trialInfo.loc[thisTrial,'scenes']   # record which scene is presented in this trial
    out.loc[thisTrial,'trial'] = thisTrial + 1   # record trial index
    
    # present fixation for isi duration
    while trialClock.getTime() < isiDur:
        core.wait(.001)
    
    # then present stimuli after fixation is done
    win.flip()   # this will flip "thisScene"
    stimClock.reset()
    # record when stimulus was prsented
    out.loc[thisTrial, 'stimOn'] = expClock.getTime()
    
    # set how long is each image presented
    while stimClock.getTime() < sceneDur:
        thisScene.draw()
        win.flip()
    
    event.clearEvents()  # clear any early response
    
    # then present question for response
    question.draw()
    win.flip()  # this will flip question
    questClock.reset()
    # record when question was presented
    out.loc[thisTrial, 'questOn'] = expClock.getTime()
    
    #set how long is question presented
    keys = []
    while questClock.getTime() < questDur:
        question.draw()
        win.flip()
    keys = event.getKeys(keyList = ["i", "o"],timeStamped = questClock)  # record responds
    print(keys)
    # save responses       
    out.loc[thisTrial, 'response'] = keys[0][0]
    out.loc[thisTrial, 'rt'] = keys[0][1]
        
        
# finish experiment
fixation.draw()
win.flip() 
core.wait(1)
 
goodby = visual.TextStim(win, text="""Thank you for participating
                         
Please get the experimenter""", height=.1)  
goodby.draw()
win.flip()
   
# manage output    
out['subj'] = subjID
out['sess'] = sessNum
out.to_csv(ouputFileName, index = False)

core.wait(3)   
       
win.close()
core.quit()
    




