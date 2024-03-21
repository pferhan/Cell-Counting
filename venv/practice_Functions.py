#def findCenter(blob)
'''    
    take x and y value and assign tempX and tempY
    set all values to 0 -> maxX, maxY, minX, minY
    for each pixel in a blob
        if (tempX > maxX)
            maxX = tempX
        else if (tempX < minX)
            minX = tempX 
        else if (tempY > maxY)
            maxY = tempY
        else (tempY < minY)
            minY = tempY
    xCenter = (minX+maxX)/2
    yCenter = (minY+maxY)/2
    make a red dot at point (xCenter, yCenter)
'''

#def drawBoxes(blob)
'''    
    use maxX, maxY, minX, minY to draw box around the whole blob
    draw line at minX and maxX from minY to maxY & draw line at minY and maxY from minX to maxX
'''