package irest;

public class LockedScreenState extends State {
    private DataManager dat = null;
    LockedScreenState(DataManager d) {
        dat = d;
    }
    
    @Override
    public void run() {
        long elapsedTime = dat.fileMgr.getElapsedTimeInSeconds();
        if (elapsedTime > dat.bigSleepTime + dat.bufferForProcessingTime) {//means computer was suspended during sleep and wakes to a locked screen state
            dat.userGotRestBy(elapsedTime);
            System.out.println("Locked scr state elapsed time: "+elapsedTime);
        } else {//normal computer lock screen state
            dat.userGotRestBy(dat.bigSleepTime);
            System.out.println("Locked scr state big sleep time: "+dat.bigSleepTime);
        }
        dat.currentState = dat.writeState;
    }    
}
