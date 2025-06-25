"""
This script shows you how to select gripper for an environment.
This is controlled by gripper_type keyword argument.
"""
import numpy as np
import robosuite as suite
from robosuite import ALL_GRIPPERS
from robosuite.environments.robot_env import RobotEnv
import argparse
import time


if __name__ == "__main__":
    # Parse command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--gripper_id",
        type=int,
        default=-1,
        help="Gripper id to use in the environment. Default is -1 (None).",
    )
    parser.add_argument(
        "--robot_name",
        type=str,
        default="Panda",
        help="Robot name to use in the environment. Default is Panda. Options: Baxter, IIWA, Jaco, Kinova3, Panda, Sawyer, UR5e.",
    )
    parser.add_argument(
        "--visualize",
        action="store_true",
        help="Whether to visualize the environment. Default is False.",
    )
    parser.add_argument(
        "-st",
        "--sim_time",
        type=float,
        default=3,
        help="Time to simulate after rendering the environment. Default is 3 seconds."
    )
    args = parser.parse_args()

    gripper = list(ALL_GRIPPERS)[args.gripper_id]
    # Notify user which gripper we're currently using
    print("Using gripper {}...".format(gripper))

    CAMERA_NAME = 'frontview'
    
    # create environment with selected grippers
    env: RobotEnv = suite.make(
        "EmptySingle",
        robots=args.robot_name,
        gripper_types=gripper,
        has_renderer=args.visualize,  # make sure we can render to the screen
        has_offscreen_renderer=False, # not needed since not using pixel obs
        use_camera_obs=False,         # do not use pixel observations
        control_freq=50,              # control should happen fast enough so that simulation looks smoother
        camera_names=CAMERA_NAME,
        deterministic_reset=True,  # use deterministic reset for reproducibility
        robot_configs=[{"xml_path": "robots/ur5e-new/robot.xml" if args.robot_name == 'UR5e' else None,}],  
    )

    # Reset the env
    obs = env.reset()
    pose = np.concatenate([obs['robot0_eef_pos'], obs['robot0_eef_quat']], axis=0)

    print("pose: {}".format(pose))
    if args.visualize:
        initial_mjstate = env.sim.get_state().flatten()
        xml = env.sim.model.get_xml()

        # add body to camera to be able to move it around
        from robosuite.scripts.tune_camera import modify_xml_for_camera_movement
        xml = modify_xml_for_camera_movement(xml, camera_name=CAMERA_NAME)
        env.reset_from_xml_string(xml)
        env.sim.reset()
        env.sim.set_state_from_flattened(initial_mjstate)
        env.sim.forward()
        
        camera_pos = np.array([1.8945960430077307, 0.019995513940986764, 0.3429729188444908])
        camera_quat = np.array([0.5, 0.50, 0.5, 0.5])
        camera_id = env.sim.model.camera_name2id(CAMERA_NAME)
        env.viewer.set_camera(camera_id=camera_id)
        cam_body_id = env.sim.model.body_name2id("cameramover")
        env.sim.model.body_pos[cam_body_id] = camera_pos
        env.sim.model.body_quat[cam_body_id] = camera_quat
        env.sim.forward()
        env.render()

        # # Get action limits
        low, high = env.action_spec
        # action = np.random.uniform(low, high)

        # Run random policy
        count = int(args.sim_time / 0.01)  # 100Hz
        for t in range(100):
            # env.render()
            action = np.zeros(*env.action_spec[0].shape) # Zero action
            observation, reward, done, info = env.step(action)
            time.sleep(0.01)

    # Close window and exit
    env.close()
    exit()