import cv2
import cvzone
import random
import mediapipe as mp
from cvzone.HandTrackingModule import HandDetector



cap = cv2.VideoCapture(0)
cap.set(3,1280)
cap.set(4,720)
detector = HandDetector(detectionCon = 0.8, maxHands=2)

bg_image = cv2.imread("Start_screen.jpg")
bg_image = cv2.resize(bg_image, (1280,720))

game_over_image = cv2.imread("Field_Background.jpg")
game_over_image = cv2.resize(game_over_image, (1280,720))



color_rect = (0, 75, 150)
color_block = (0, 0, 255)


cx, cy, w , h = 100 ,100 ,200 ,200

#Falling Blocks
block_size = 50
blocks = []

#Start of Game Settings
score = 0
lives = 3
game_over = False
state = 'title'

def create_block():
    return {
        "x": random.randint(0, 1280 - block_size), "y": -block_size, "speed": random.randint(2,4)
    }

def start_screen(img):
    img[:] = bg_image 
    title_font = cv2.FONT_HERSHEY_DUPLEX
    thickness_border = 6
    title_text = "Catch The Apples"
    start_text = "Press P to Play"

    cv2.putText(img, title_text, (300, 300), title_font, 2, (0, 0, 0), thickness_border, cv2.LINE_AA)
    cv2.putText(img, title_text, (300, 300), title_font, 2, (0, 0, 255), 4, cv2.LINE_AA)

    cv2.putText(img, start_text, (460, 400), title_font, 1, (0, 0, 0), thickness_border, cv2.LINE_AA)
    cv2.putText(img, start_text, (460, 400), title_font, 1, (19, 69, 139), 2, cv2.LINE_AA)

def game_over_screen(img):
    img[:] = game_over_image
    font = cv2.FONT_HERSHEY_DUPLEX
    thickness_border = 6
    cv2.putText(img, 'GAME OVER', (300, 360), cv2.FONT_HERSHEY_DUPLEX, 3, (0, 0, 0),thickness_border, 4)
    cv2.putText(img, 'GAME OVER', (300, 360), cv2.FONT_HERSHEY_DUPLEX, 3, (0, 0, 255), 4)

    cv2.putText(img, 'Press R to Restart', (460, 460), cv2.FONT_HERSHEY_DUPLEX, 1, (0, 0, 0), thickness_border, cv2.LINE_AA)
    cv2.putText(img, 'Press R to Restart', (460, 460), cv2.FONT_HERSHEY_DUPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)




class DragRect():
    def __init__(self,posCenter, size=[175,175]):
        self.posCenter = posCenter
        self.size = size

    def update(self,cursor):
        cx,cy = self.posCenter
        w, h = self.size

        # IF the index finger tip is in the rectangle region
        if cx-w//2 < cursor[0] < cx+w//2 and cy-h//2 < cursor[1]< cy+h//2:
                    self.posCenter = cursor
                    color_rect = (0,0,0)
        else:
            color_rect = (0,75,150)




player_rect = DragRect([640,400])

while True:
    success, img = cap.read()
    img = cv2.flip(img, 1)

    if not success:
        print("Failed to Capture Image")
        break
    if state == 'title':
        start_screen(img)

        if cv2.waitKey(1) & 0xFF == ord('p'):
            state = "game"
    
    elif state == 'game':
        game_over = False
        hands, img = detector.findHands(img, flipType=False, draw=False) # With Draw

        if hands:
            hand = hands[0]
            for hand in hands:
                lm_list = hand['lmList']
                if len(lm_list) > 12: 
                    cursor = lm_list[8][:2]
                    middle_tip = lm_list[12][:2]

                    l, _, _ = detector.findDistance(cursor, middle_tip)
                    
                    
                    if l < 65:
                        # call the update her
                        player_rect.update(cursor)
        if not game_over and len(blocks) < 5:
            blocks.append(create_block())

        # Collision with Blocks
        for block in blocks:
            block['y'] += block['speed']
            if block['y'] > 720: # Bottom Of Screen
                lives -= 1
                blocks.remove(block)
            else:
                block_rect_x1 = block['x']
                block_rect_y1 = block['y']
                block_rect_x2 = block['x'] + block_size
                block_rect_y2 = block['y'] + block_size

    
                rect_x1 = player_rect.posCenter[0] - player_rect.size[0] // 2
                rect_y1 = player_rect.posCenter[1] - player_rect.size[1] // 2
                rect_x2 = player_rect.posCenter[0] + player_rect.size[0] // 2
                rect_y2 = player_rect.posCenter[1] + player_rect.size[1] // 2

                if (rect_x1 < block_rect_x2 and rect_x2 > block_rect_x1 and rect_y1 < block_rect_y2 and rect_y2 > block_rect_y1):
                    score += 1
                    blocks.remove(block)
        
        # Spawn in moving Blocks
        for block in blocks:
            cv2.rectangle(img, (block["x"], block["y"]), (block["x"] + block_size, block["y"] + block_size), color_block, cv2.FILLED)

        #Same as Draw
    
        cx, cy = player_rect.posCenter
        w,h = player_rect.size
        cv2.rectangle(img, (cx-w//2,cy-h//2),(cx+w//2, cy+h//2), (color_rect), cv2.FILLED)

        cvzone.cornerRect(img, (cx-w//2, cy-h//2, w, h),20, rt =0 , colorC = (255,255,255))
    
    
        
    
        #TEXT ON SCREEN
        score_text = f'Score: {score}'
        lives_text = f'Lives: {lives}'

        score_color = (0,248,255)
        lives_color = (0,255,18)

        outline_color = (0,0,0)

        shadow_offset = 2

        score_position = (30,50)
        lives_position = (30,100)

        cv2.putText(img, score_text, (score_position[0] + shadow_offset, score_position[1] + shadow_offset), cv2.FONT_HERSHEY_SIMPLEX, 1, outline_color, 2, cv2.LINE_AA)
        cv2.putText(img, lives_text, (lives_position[0] + shadow_offset, lives_position[1] + shadow_offset), cv2.FONT_HERSHEY_SIMPLEX, 1, outline_color, 2, cv2.LINE_AA)

        cv2.putText(img, score_text, score_position, cv2.FONT_HERSHEY_SIMPLEX, 1, score_color, 2, cv2.LINE_AA)
        cv2.putText(img, lives_text, lives_position, cv2.FONT_HERSHEY_SIMPLEX, 1, lives_color, 2, cv2.LINE_AA)




        if lives <= 0:
            lives = 0
            game_over = True
            state = 'game_over'

    elif state == 'game_over':
        game_over_screen(img)


        if cv2.waitKey(1) & 0xFF == ord("r"):
            score = 0
            lives = 3
            blocks.clear()
            state = "game"


    cv2.imshow("Image", img ) 

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
    

cap.release()
cv2.destroyAllWindows()
