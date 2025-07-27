import cv2
import numpy as np
from pathlib import Path

class Pixel2CM:
    def __init__(self):
        self.HomePath = Path.home()

        self.CamPorts = [0,2,4,6]

        self.PerspectiveMatrices = []
        self.P2CK = []
        self.P2CHB = []
        self.P2CVB = []


        for i in range(4):
            NumpyData = np.load(self.HomePath / f'CalibrationData{self.CamPorts[i]}.npz')
            PerspectiveMatrix = NumpyData['matrix']
            self.PerspectiveMatrices.append(PerspectiveMatrix)
            P2CK = NumpyData['p2c'][0]
            self.P2CK.append(P2CK)
            P2CHB = NumpyData['p2c'][1]
            self.P2CHB.append(P2CHB)
            P2CVB = NumpyData['p2c'][2]
            self.P2CVB.append(P2CVB)
    
    def ApplyPerspectiveTransform(self,X, Y, Matrix):
        Point = np.array([X, Y, 1], dtype=np.float64)
        Transformed = Matrix @ Point
        Transformed /= Transformed[2]
        return int(Transformed[0]), int(Transformed[1])

    def Pixel2CM(self,X,Y,CamIndex):
        P2CK = self.P2CK[CamIndex]
        P2CHB = self.P2CHB[CamIndex]
        P2CVB = self.P2CVB[CamIndex]

        X, Y = self.ApplyPerspectiveTransform(X, Y, self.PerspectiveMatrices[CamIndex])

        X = int(self.P2CK[CamIndex] * X + self.P2CHB[CamIndex])
        Y = int(-self.P2CK[CamIndex] * Y + self.P2CVB[CamIndex])

        return X, Y
    
    def CM2Pixel(self, X, Y, CamIndex):
        P2CK = self.P2CK[CamIndex]
        P2CHB = self.P2CHB[CamIndex]
        P2CVB = self.P2CVB[CamIndex]

        X = (X - P2CHB) / P2CK
        Y = -(Y - P2CVB) / P2CK

        X, Y = self.ApplyPerspectiveTransform(X, Y, np.linalg.inv(self.PerspectiveMatrices[CamIndex]))

        return int(X), int(Y)