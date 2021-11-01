package irest;

public class ActiveState extends State {
    private DataManager dat = null;    
    ActiveState(DataManager d) {
        dat = d;
    }
    
    @Override
    public void run() {
        long elapsedTime = dat.fileMgr.getElapsedTimeInSeconds();
        if (elapsedTime > dat.bigSleepTime + dat.bufferForProcessingTime) {//means computer was suspended during sleep
            dat.userGotRestBy(elapsedTime);
            System.out.println("Active state elapsed time: "+elapsedTime);
        } else {//normal computer active state
            dat.userWasStrainedBy(dat.bigSleepTime);
            System.out.println("Active state bigSleep time: "+dat.bigSleepTime);
        }
        
        dat.currentState = dat.writeState;        
    }
}
