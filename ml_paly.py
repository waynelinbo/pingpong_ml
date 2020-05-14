"""
The template of the script for the machine learning process in game pingpong
"""
# Import the necessary modules and classes
from mlgame.communication import ml as comm

def ml_loop(side: str):
    """
    The main loop for the machine learning process

    The `side` parameter can be used for switch the code for either of both sides,
    so you can write the code for both sides in the same script. Such as:
    ```python
    if side == "1P":
        ml_loop_for_1P()
    else:
        ml_loop_for_2P()
    ```

    @param side The side which this script is executed for. Either "1P" or "2P".
    """

    # === Here is the execution order of the loop === #
    # 1. Put the initialization code here
    ball_served = False
    blocker = 0
    blocker_direction = False
    blocker_y = 240
    blocker_length = 30
    ball_length = 5
    is_cal = False
    final_x = 100

    def block_next(block, bd):
        if bd == True:
                block -= 5
                if(block == 0):
                    bd = False # right
        else:
            block += 5
            if(block == 170):
                    bd = True # left
        return [block, bd]
    """
    def move_to(player, pred) : #move platform to predicted position to catch ball 
        if player == '1P':
            #if scene_info["platform_1P"][0]+20  > (pred-10) and scene_info["platform_1P"][0]+20 < (pred+10): return 0 # NONE
            if scene_info["platform_1P"][0]+20  == pred: return 0 # NONE
            elif scene_info["platform_1P"][0]+20 <= (pred) : return 1 # goes right
            else : return 2 # goes left
        else :
            if scene_info["platform_2P"][0]+20  > (pred-10) and scene_info["platform_2P"][0]+20 < (pred+10): return 0 # NONE
            elif scene_info["platform_2P"][0]+20 <= (pred-10) : return 1 # goes right
            else : return 2 # goes left
    """

    def move_to(player, pred) : #move platform to predicted position to catch ball 
        if player == '1P':
            if scene_info["platform_1P"][0]+20  > (pred-10) and scene_info["platform_1P"][0]+20 < (pred+10): return 0 # NONE
            elif scene_info["platform_1P"][0]+20 <= (pred-10) : return 1 # goes right
            else : return 2 # goes left
        else :
            if scene_info["platform_2P"][0]+20  > (pred-10) and scene_info["platform_2P"][0]+20 < (pred+10): return 0 # NONE
            elif scene_info["platform_2P"][0]+20 <= (pred-10) : return 1 # goes right
            else : return 2 # goes left

    def ml_loop_for_1P():
        if scene_info["ball_speed"][1] > 0:
            c_y = scene_info["ball"][1]
            c_x = scene_info["ball"][0]
            c_speed = [scene_info["ball_speed"][0],scene_info["ball_speed"][1]]
            c_frame = scene_info["frame"]
            c_blocker = blocker
            c_bd = blocker_direction
            while True: # 模擬
                c_frame+=1
                l_y = c_y
                l_x = c_x
                c_y += c_speed[1]
                c_x += c_speed[0]
                c_yd = False
                c_xd = False
                if(c_speed[1] > 0):
                    c_yd = False
                else:
                    c_yd = True
                if(c_speed[0] > 0):
                    c_xd = False
                else:
                    c_xd = True
                
                [c_blocker, c_bd] = block_next(c_blocker, c_bd)
                if(c_x+ball_length >= c_blocker) and (c_x <= c_blocker + blocker_length): #block相交
                    if (l_y+ball_length < blocker_y): #原本在障礙物上方
                        if (c_y >= blocker_y) and ((c_x+ball_length > c_blocker + blocker_length) or (c_x < c_blocker)) : #上下完全陷進去 且 左右差一點進去
                            c_speed[0] = -c_speed[0]
                            if c_xd : #原本球往左飛
                                c_x = c_blocker+blocker_length
                            else :
                                c_x = c_blocker - ball_length
                        else:
                            return -1
                    elif (l_y+ball_length > blocker_y) and (l_y < blocker_y+20) and (c_y < blocker_y+30): #原本同障礙物y 現在下去
                                c_speed[0] = -c_speed[0]
                                if c_xd : #原本球往左飛
                                    c_x = c_blocker+blocker_length
                                else :
                                    c_x = c_blocker - ball_length

                if (c_y+ball_length >= 420): #到板子了
                    if c_x >= 195:
                        c_x = 195
                        c_speed[0] = -c_speed[0]
                    elif c_x <= 0:
                        c_x = 0
                        c_speed[0] = -c_speed[0]
                    return  c_x
                else:#撞牆
                    if c_x >= 195:
                        c_x = 195
                        c_speed[0] = -c_speed[0]
                    elif c_x <= 0:
                        c_x = 0
                        c_speed[0] = -c_speed[0]

                # c_speed[1]
                if(c_yd):
                    c_speed[1] = 0 - int((c_frame-1)/100)+7
                else:
                    c_speed[1] = int((c_frame-1)/100)+7
        else:
            return  -1

    """def ml_loop_for_2P():
        pass"""
        

    # 2. Inform the game process that ml process is ready
    comm.ml_ready()

    # 3. Start an endless loop
    while True:
        # 3.1. Receive the scene information sent from the game process
        scene_info = comm.recv_from_game()
        
        if(scene_info["ball_speed"][1] < 0):
            is_cal = False
        
        if(scene_info["frame"] == 0):
            blocker = scene_info["blocker"][0]
            is_cal = False
        elif(scene_info["frame"] == 1):
            temp = blocker
            blocker = scene_info["blocker"][0]
            if blocker == 0:
                blocker_direction = False # right
            elif blocker == 170:
                blocker_direction = True  # left
            elif blocker - temp > 0:
                blocker_direction = False # right
            else:
                blocker_direction = True  # left
        else:
            [blocker, blocker_direction] = block_next(blocker, blocker_direction)
        
        print(blocker)
        

        # 3.2. If either of two sides wins the game, do the updating or
        #      resetting stuff and inform the game process when the ml process
        #      is ready.
        if scene_info["status"] != "GAME_ALIVE":
            # Do some updating or resetting stuff
            ball_served = False

            # 3.2.1 Inform the game process that
            #       the ml process is ready for the next round
            comm.ml_ready()
            continue

        # 3.3 Put the code here to handle the scene information

        # 3.4 Send the instruction for this frame to the game process
        if not ball_served:
            comm.send_to_game({"frame": scene_info["frame"], "command": "SERVE_TO_LEFT"})
            ball_served = True
        else:
            if side == "1P":
                if(is_cal == True):
                    command = move_to(player = '1P',pred = final_x)
                else:
                    a = ml_loop_for_1P()
                    if a > 0:
                        final_x = a
                        command = move_to(player = '1P',pred = final_x)
                        is_cal = True
                    else:
                        command = move_to(player = '1P',pred = 100)
            """else:
                command = ml_loop_for_2P()"""

            if command == 0:
                comm.send_to_game({"frame": scene_info["frame"], "command": "NONE"})
            elif command == 1:
                comm.send_to_game({"frame": scene_info["frame"], "command": "MOVE_RIGHT"})
            else :
                comm.send_to_game({"frame": scene_info["frame"], "command": "MOVE_LEFT"})
