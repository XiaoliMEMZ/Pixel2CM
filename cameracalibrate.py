import cv2
import numpy as np
import time
import math
from pathlib import Path

CamIndex = 0
# Change your camera index here
Intercept = 16.5
# The distance from the chessboard's lower-left corner of the bottom rank to the robot’s


Cam = cv2.VideoCapture(CamIndex,cv2.CAP_V4L2)
Cam.set(cv2.CAP_PROP_AUTO_EXPOSURE, 1)
Cam.set(cv2.CAP_PROP_BRIGHTNESS, -64)
Cam.set(cv2.CAP_PROP_CONTRAST, 32)
Cam.set(cv2.CAP_PROP_SATURATION, 64)
Cam.set(cv2.CAP_PROP_SHARPNESS, 2)
# Ensure the exposure is the lowest

def applyPerspectiveTransform(X, Y, Matrix):
    Point = np.array([X, Y, 1], dtype=np.float64)
    Transformed = Matrix @ Point
    Transformed /= Transformed[2]
    return int(Transformed[0]), int(Transformed[1])


time.sleep(2)
_,Frame = Cam.read()
while True:
    _,Frame = Cam.read()
    cv2.imshow("Frame", Frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
Gray = cv2.cvtColor(Frame, cv2.COLOR_BGR2GRAY)
# Adjust the chessboard and press q

Ret,Corners = cv2.findChessboardCornersSB(Gray, (9, 9), None)
# Use Structured Binary for robustness

# Auto save to /root/CalibrationDataX.npz
if Corners is not None:
    HomePath = Path.home()
    lCorners = [(Corners[72][0][0],Corners[72][0][1]),(Corners[0][0][0],Corners[0][0][1]),(Corners[80][0][0],Corners[80][0][1]),(Corners[8][0][0],Corners[8][0][1])]
    lCorners.sort(key=lambda item: item[0])
    print(lCorners)
    fBottomY = (lCorners[0][1] + lCorners[3][1]) / 2

    fDistance = math.sqrt((lCorners[0][0] - lCorners[3][0])**2 + (lCorners[0][1] - lCorners[3][1])**2)
    fPixelToCM = 12 / fDistance
    

    fHorizontalSlope = (lCorners[0][1] - lCorners[3][1]) / (lCorners[0][0] - lCorners[3][0])
    fVerticalSlope = -1 / fHorizontalSlope
    if fVerticalSlope > 0:
        iTheta = math.atan(fVerticalSlope)
    else:
        iTheta = math.atan(fVerticalSlope) + math.pi
    fDeltaX = math.cos(iTheta) * fDistance
    fDeltaY = math.sin(iTheta) * fDistance
    fCorrectedLFX = lCorners[0][0] + fDeltaX
    fCorrectedLFY = lCorners[0][1] - fDeltaY
    fCorrectedRFX = lCorners[3][0] + fDeltaX
    fCorrectedRFY = lCorners[3][1] - fDeltaY
    # print(fCorrectedLFX,fCorrectedLFY,fCorrectedRFX,fCorrectedRFY)
    print(lCorners[0],(fCorrectedLFX,fCorrectedLFY),(fCorrectedRFX,fCorrectedRFY),lCorners[3])

    lSRCPoints = np.float32(lCorners)
    lDSTPoints = np.float32([lCorners[0],(fCorrectedLFX,fCorrectedLFY),(fCorrectedRFX,fCorrectedRFY),lCorners[3]])

    aPerspectiveMatrix = cv2.getPerspectiveTransform(lSRCPoints,lDSTPoints)
    print(aPerspectiveMatrix)
    print(fPixelToCM)
    print(fBottomY)
    iX,iY = applyPerspectiveTransform(320,fBottomY,aPerspectiveMatrix)
    fHorizontalB = -fPixelToCM * iX
    fVerticalB = Intercept + fPixelToCM * iY

    aPixelToCM = np.array([fPixelToCM,fHorizontalB,fVerticalB])
    print(fVerticalB)
    # print(applyPerspectiveTransform(320,240,aPerspectiveMatrix))

    np.savez(HomePath / f'CalibrationData{CamIndex}.npz', 
            matrix=aPerspectiveMatrix, 
            p2c=aPixelToCM)



