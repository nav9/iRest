package irest;

import java.util.logging.Level;
import java.util.logging.Logger;

public class SmallSleepState extends State {
    private DataManager dat = null;
    SmallSleepState(DataManager d) {
        dat = d;
    }
    
    @Override
    public void run() {
        dat.fileMgr.writeToFileByOverwriting();//for saving the lastActiveTime 
        System.out.println("going for small sleep");
        try {
            Thread.sleep(dat.getSmallSleepTimeInMillis());//go to sleep for 1 minute
        } catch (InterruptedException ex) {Logger.getLogger(SmallSleepState.class.getName()).log(Level.SEVERE, null, ex);}
        
        long elapsedTime = dat.fileMgr.getElapsedTimeInSeconds();
        if (elapsedTime > dat.smallSleepTime + dat.bufferForProcessingTime) {//means computer was suspended during sleep
            dat.userGotRestBy(elapsedTime);//user was getting rest            
        } else {//user is using computer inspite of reminder
            dat.userWasStrainedBy(dat.smallSleepTime);//user was straining eyes more than necessary
        }
        
        dat.currentState = dat.writeState;//next state to switch to
    }
}
