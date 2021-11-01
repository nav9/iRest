package irest;

import linux.LinuxScreenLockDetect;

public class DataManager {
    public State currentState = new State();
    public BigSleepState bigSleepState = null;
    public SmallSleepState smallSleepState = null;
    public LockedScreenState lockedScreenState = null;
    public ActiveState activeState = null;
    public StartState startState = null;
    public WriteAndDecideState writeState = null;
    public ReminderState reminderState = null;

    private LockScreenDetector lockScreen = new LockScreenDetector();//Default functionality is to not detect lock screen. Can be overridden based on OS type, where the overriding class can detect screen locks
    private final int toMilli = 1000;
    private final int toSecond = 60;
    private final int maxTolerableStrainTime = 60 * toSecond;//Unit: seconds
    public final long bufferForProcessingTime = 5;//Unit: seconds
    public final int bigSleepTime = 5 * toSecond;//Unit: seconds
    public final int smallSleepTime = 1 * toSecond;//Unit: seconds
    
    public StrainTracker strainInfo = null;
    public FileManager fileMgr = null;
    
    DataManager() {
        strainInfo = new StrainTracker();
        fileMgr = new FileManager(strainInfo);
    
        String osName = System.getProperty("os.name");
        //---Assign lock screen detection class based on OS type
        if (osName.equals("Linux")) {lockScreen = new LinuxScreenLockDetect();}
        //TODO: add line for windows lock screen detection and for Mac 
    }//ctor
    
    public final int getBigSleepTimeInMillis() { return bigSleepTime * toMilli; }
    public final int getSmallSleepTimeInMillis() { return smallSleepTime * toMilli; }
    
    public void createStatesAndStart() {
        bigSleepState = new BigSleepState(this);
        smallSleepState = new SmallSleepState(this);
        lockedScreenState = new LockedScreenState(this);
        activeState = new ActiveState(this);
        startState = new StartState(this);
        writeState = new WriteAndDecideState(this);
        reminderState = new ReminderState(this);  
        
        currentState = bigSleepState;//assign the state to start with
    }
    
    public boolean isScreenLocked() {return lockScreen.isScreenLocked();}
    
    public void userGotRestBy(final double time) {
        System.out.println("User got rest by:"+ time+". Rate of strain decr: "+strainInfo.rateOfStrainDecrease);
        strainInfo.secondsUserIsStrained -= time * strainInfo.rateOfStrainDecrease;//user was getting rest
        if (strainInfo.secondsUserIsStrained < 0) {strainInfo.secondsUserIsStrained = 0;}
    }

    public void userWasStrainedBy(final double time) {
        System.out.println("User was strained by:"+ time+". Rate of strain incr: "+strainInfo.rateOfStrainIncrease);
        strainInfo.secondsUserIsStrained += time * strainInfo.rateOfStrainIncrease;//user was being strained
    }
    
    public boolean userNeedsToBeRemindedToStop() {    
        System.out.println("secondsStrained:"+strainInfo.secondsUserIsStrained+". maxTolerableStrainTime:"+maxTolerableStrainTime);
        return strainInfo.secondsUserIsStrained >= maxTolerableStrainTime;
    }
    
}
