import sys
import os
import numpy as np
import re

"""
CSV DATA:
Timestamp,ImageFileName,
Position.X,Position.Y,Position.Z,
Orientation.W,Orientation.X,Orientation.Y,Orientation.Z,
FrameToOrigin.m11,FrameToOrigin.m12,FrameToOrigin.m13,FrameToOrigin.m14,
FrameToOrigin.m21,FrameToOrigin.m22,FrameToOrigin.m23,FrameToOrigin.m24,
FrameToOrigin.m31,FrameToOrigin.m32,FrameToOrigin.m33,FrameToOrigin.m34,
FrameToOrigin.m41,FrameToOrigin.m42,FrameToOrigin.m43,FrameToOrigin.m44,
CameraViewTransform.m11,CameraViewTransform.m12,CameraViewTransform.m13,CameraViewTransform.m14,
CameraViewTransform.m21,CameraViewTransform.m22,CameraViewTransform.m23,CameraViewTransform.m24,
CameraViewTransform.m31,CameraViewTransform.m32,CameraViewTransform.m33,CameraViewTransform.m34,
CameraViewTransform.m41,CameraViewTransform.m42,CameraViewTransform.m43,CameraViewTransform.m44,
CameraProjectionTransform.m11,CameraProjectionTransform.m12,CameraProjectionTransform.m13,CameraProjectionTransform.m14,
CameraProjectionTransform.m21,CameraProjectionTransform.m22,CameraProjectionTransform.m23,CameraProjectionTransform.m24,
CameraProjectionTransform.m31,CameraProjectionTransform.m32,CameraProjectionTransform.m33,CameraProjectionTransform.m34,
CameraProjectionTransform.m41,CameraProjectionTransform.m42,CameraProjectionTransform.m43,CameraProjectionTransform.m44

Vicon transform:
t1 t2 t3 rho S1 S2 S3 d1 d2 d3
"""

def quaternion_to_matrix(q):
    R = np.zeros((3,3))
    qw = q[0]
    qx = q[1]
    qy = q[2]
    qz = q[3]

    R[0][0] = 1 - 2 * qy * qy - 2 * qz * qz
    R[0][1] = 2 * qx * qy - 2 * qz * qw
    R[0][2] = 2 * qx * qz + 2 * qy * qw

    R[1][0] = 2 * qx * qy + 2 * qz * qw
    R[1][1] = 1 - 2 * qx * qx - 2 * qz * qz
    R[1][2] = 2 * qy * qz - 2 * qx * qw

    R[2][0] = 2 * qx * qz - 2 * qy * qw
    R[2][1] = 2 * qy * qz + 2 * qx * qw
    R[2][2] = 1 - 2 * qx * qx - 2 * qy * qy

    return R


folder = sys.argv[1]
csvfilepath = sys.argv[2]
viconTransform = sys.argv[3]

print(folder)

if not folder[-1] == '/':
    folder = folder + '/'

csvfile = open(csvfilepath, 'r')
csvheader = csvfile.readline()
print(csvheader)
csvdata = csvfile.read()
csvfile.close()

parsedcsvdata = csvdata.split("\n")
parsedcsvdata = [x for x in parsedcsvdata if x]
camerainfo = {}
for csvline in parsedcsvdata:
    splitted = csvline.split(",")
    name = splitted[1].split("\\")[-1].split(".")[0]
    camerainfo[name] = csvline

vicontrfile = open(viconTransform, 'r')
rho = float(vicontrfile.readline())

St1 = vicontrfile.readline().split(' ')
St2 = vicontrfile.readline().split(' ')
St3 = vicontrfile.readline().split(' ')
St = np.array([[float(St1[0]), float(St1[1]), float(St1[2])],[float(St2[0]), float(St2[1]), float(St2[2])],[float(St3[0]), float(St3[1]), float(St3[2])]])

Rii1 = vicontrfile.readline().split(' ')
Rii2 = vicontrfile.readline().split(' ')
Rii3 = vicontrfile.readline().split(' ')
Riniticp = np.array([[float(Rii1[0]), float(Rii1[1]), float(Rii1[2])],[float(Rii2[0]), float(Rii2[1]), float(Rii2[2])],[float(Rii3[0]), float(Rii3[1]), float(Rii3[2])]])

x = float(vicontrfile.readline())
y = float(vicontrfile.readline())
z = float(vicontrfile.readline())

T = np.array([x, y, z])

vicontrfile.close()

outfile = open(folder + 'out.obj', 'w')
objcount = 1


for r, d, f in os.walk(folder):
    print(f)
    for file in f:
        match = re.search('world_', file)
        #print("Processing file: " + file)
        if '.obj' in file and file != "out.obj" and match is None:
            print("Processing file: " + file)
            name = file.split(".")[0]
            objfile = open(r + file, 'r')
            objfile.readline()
            objdata = objfile.read()
            objlines = objdata.split("\n")
            objlines = [x.split("v ")[1] for x in objlines if x]
            objfile.close()

            outfile.write('o Object.' + str(objcount) + "\n")
            objcount = objcount + 1

            poseinfo = camerainfo[name]
            poseinfo = poseinfo.split(",")
            position = np.array([float(poseinfo[2]), float(poseinfo[3]), float(poseinfo[4])])
            quaternion = np.array([float(poseinfo[5]), float(poseinfo[6]), float(poseinfo[7]), float(poseinfo[8])])
            rotation = quaternion_to_matrix(quaternion)

            frametoorigin = np.array([[float(poseinfo[9]), float(poseinfo[10]), float(poseinfo[11]), float(poseinfo[12])],
                                      [float(poseinfo[13]), float(poseinfo[14]), float(poseinfo[15]), float(poseinfo[16])],
                                      [float(poseinfo[17]), float(poseinfo[18]), float(poseinfo[19]), float(poseinfo[20])],
                                      [float(poseinfo[21]), float(poseinfo[22]), float(poseinfo[23]), float(poseinfo[24])]])

            cameraviewtransform = np.array([[float(poseinfo[25]), float(poseinfo[26]), float(poseinfo[27]), float(poseinfo[28])],
                                      [float(poseinfo[29]), float(poseinfo[30]), float(poseinfo[31]), float(poseinfo[32])],
                                      [float(poseinfo[33]), float(poseinfo[34]), float(poseinfo[35]), float(poseinfo[36])],
                                      [float(poseinfo[37]), float(poseinfo[38]), float(poseinfo[39]), float(poseinfo[40])]])

            cameraprojectiontransform = np.array([[float(poseinfo[41]), float(poseinfo[42]), float(poseinfo[43]), float(poseinfo[44])],
                                      [float(poseinfo[45]), float(poseinfo[46]), float(poseinfo[47]), float(poseinfo[48])],
                                      [float(poseinfo[49]), float(poseinfo[50]), float(poseinfo[51]), float(poseinfo[52])],
                                      [float(poseinfo[53]), float(poseinfo[54]), float(poseinfo[55]), float(poseinfo[56])]])

            # save transformed point cloud in world coordinate system
            localoutfile = open(r + 'world_' + file, 'w')
            localoutfile.write("o Object.1\n")

            for line in objlines:
                parsed = line.split(" ")
                #coords = np.array([float(parsed[0]), float(parsed[1]), float(parsed[2]), 0])
                #coords = np.array([float(parsed[0]), float(parsed[1]), float(parsed[2])])
                #newcoords = np.matmul(rotation, np.transpose(coords)) + np.transpose(position)
                #newcoords = np.matmul(np.matmul(frametoorigin, cameraviewtransform), np.transpose(coords))
                coords = np.array([float(parsed[0]), float(parsed[1]), float(parsed[2])]) + position
                newcoords = np.matmul(1 / rho * St, np.transpose(np.matmul(coords, Riniticp))) + np.transpose(T)

                localoutfile.write("v " + str(newcoords[0]) + " " + str(-1 * newcoords[1]) + " " + str(newcoords[2]) + "\n")
                outfile.write("v " + str(newcoords[0]) + " " + str(-1 * newcoords[1]) + " " + str(newcoords[2]) + "\n")

            localoutfile.write("\n")
            localoutfile.close()
            outfile.write("\n")

outfile.close()
