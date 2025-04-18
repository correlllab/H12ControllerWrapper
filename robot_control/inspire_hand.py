
from unitree_dds_wrapper.idl import unitree_go
from unitree_dds_wrapper.publisher import Publisher
from unitree_dds_wrapper.subscription import Subscription
import numpy as np
import threading
import time


class H1HandController:
    def __init__(self):
        self.cmd = unitree_go.msg.dds_.MotorCmds_()
        self.state = unitree_go.msg.dds_.MotorStates_()
        self.labels = {
            "open": np.ones(6),
            "close": np.zeros(6),
            "half": np.full(6, 0.5)
        }
        self.lock = threading.Lock()
        self.init_dds()

    def init_dds(self):
        self.handcmd = Publisher(unitree_go.msg.dds_.MotorCmds_, "rt/inspire/cmd")
        self.handstate = Subscription(unitree_go.msg.dds_.MotorStates_, "rt/inspire/state")
        self.cmd.cmds = [unitree_go.msg.dds_.MotorCmd_() for _ in range(12)]
        self.state.states = [unitree_go.msg.dds_.MotorState_() for _ in range(12)]

        self.report_rpy_thread = threading.Thread(target=self.subscribe_state)
        self.report_rpy_thread.start()

    def subscribe_state(self):
        while True:
            if self.handstate.msg:
                self.state = self.handstate.msg
            time.sleep(0.01)

    def ctrl(self, label):
        if label in self.labels:
            self._ctrl(self.labels[label], self.labels[label])
        else:
            print(f"Invalid label: {label}")

    def crtl(self,right_angles,left_angles):
        self._ctrl(right_angles,left_angles)

    def _ctrl(self, right_angles, left_angles):
        for i in range(6):
            self.cmd.cmds[i].q = right_angles[i]
            self.cmd.cmds[i+6].q = left_angles[i]
        self.handcmd.msg.cmds = self.cmd.cmds
        self.handcmd.write()

    def get_hand_state(self):
        with self.lock:
            q = np.array([self.state.states[i].q for i in range(12)])
            return q
        
    def get_right_q(self):
        with self.lock:
            q = np.array([self.state.states[i].q for i in range(6)])
            return q

    def get_left_q(self):
        with self.lock:
            q = np.array([self.state.states[i+6].q for i in range(6)])
            return q

if __name__ == "__main__":
    print("begining robot_hand.py main")
    controller = H1HandController()
    print("controller created")
    controller.crtl(controller.labels["open"], controller.labels["open"])
    input("Press Enter to play hand animation...")
    try:
        while True:
            l_hand = [np.sin(i+time.time()) for i in range(5)] + [1]
            r_hand = [np.cos(i+time.time()) for i in range(5)] + [1]
            controller.crtl(l_hand, r_hand)
            time.sleep(0.1)
            #test_array = np.ones(6)
            #test_array[5] = 0
            #$controller.crtl(test_array, controller.labels["open"])
            #controller.crtl(controller.labels["close"], controller.labels["close"])
            
            #print("closed")
            #time.sleep(1)
    except KeyboardInterrupt:
        print("Exiting...")

#vector 0 being closed and 1 being open
#index 0:pinky
#index 1:ring
#index 2:middle
#index 3:index
#index 4:thumb
#index 5:thumb angle
