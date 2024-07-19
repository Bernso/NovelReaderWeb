chapter = 'Chapter 534: Metamorphosis (4) '
chapter = chapter[8:] # Remove chapter from text
chapterNumber = ''  # Prepare the variable
for character in chapter: # Cycle through each charcter
    print(chapterNumber) # print out the current chapter number (for debugging)
    if character.isnumeric(): # Check if character is a number
        if not len(chapterNumber) >= 4: # Check if the chaper number is not 10,000 or over
            chapterNumber += character # Add number to chapter number
    else:
        break # If the character is not a number it will stop
chapterNumber = int(chapterNumber) # Convert to an int so it cna be used in the for loop later
print(f"The number of chapters: {chapterNumber}") # Check its working