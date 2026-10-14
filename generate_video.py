import json, os, random, subprocess, textwrap
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

OUT = Path("output")
OUT.mkdir(exist_ok=True)
W, H = 720, 1280
FONT_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_REG = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

STORIES = [
    {"title":"Milo Shares the Stars", "lines":["Milo the little bear looked up at the sky.","He shared his star-shaped cookies with a shy friend.","Kindness made their whole night sparkle!"], "lesson":"Sharing makes friendship shine."},
    {"title":"Pippa and the Little Rain Cloud", "lines":["Pippa found a tiny cloud feeling blue.","She danced in the garden and watered every flower.","Soon the garden smiled with colorful blooms!"], "lesson":"Even small help can make a big difference."},
    {"title":"Toto Learns to Take Turns", "lines":["Toto wanted to play with the big red ball.","He waited while his friends each had a turn.","Then everyone played together and laughed!"], "lesson":"Taking turns helps everyone have fun."},
    {"title":"Nina's Brave Little Step", "lines":["Nina was nervous to cross the wobbly bridge.","Her friend cheered as she took one careful step.","Nina reached the other side and felt proud!"], "lesson":"Being brave can start with one small step."},
]

def font(size, bold=True):
    path = FONT_PATH if bold else FONT_REG
    try: return ImageFont.truetype(path, size)
    except OSError: return ImageFont.load_default()

def centered(draw, text, y, fnt, fill, max_width=640):
    words=text.split(); lines=[]; current=''
    for word in words:
        test=(current+' '+word).strip()
        if draw.textbbox((0,0),test,font=fnt)[2] <= max_width: current=test
        else:
            if current: lines.append(current)
            current=word
    if current: lines.append(current)
    for line in lines:
        box=draw.textbbox((0,0),line,font=fnt); x=(W-(box[2]-box[0]))//2
        draw.text((x,y),line,font=fnt,fill=fill,stroke_width=2,stroke_fill=(70,70,90))
        y += fnt.size+12

def scene(path, title, caption, index):
    palettes=[((150,218,255),(255,239,172),(92,190,128)),((255,208,220),(255,244,190),(102,185,154)),((190,226,255),(255,223,160),(119,193,126))]
    sky,sun,grass=palettes[index%len(palettes)]
    im=Image.new('RGB',(W,H),sky); d=ImageDraw.Draw(im)
    # sun and soft clouds
    d.ellipse((540,90,650,200),fill=sun)
    for cx,cy in [(130,160),(360,230),(560,300)]:
        d.ellipse((cx-60,cy,cx+15,cy+50),fill=(255,255,255)); d.ellipse((cx-20,cy-25,cx+50,cy+45),fill=(255,255,255)); d.ellipse((cx+15,cy,cx+80,cy+50),fill=(255,255,255))
    d.ellipse((-120,660,420,1000),fill=grass); d.ellipse((280,650,850,1040),fill=grass)
    # cute bear face/body
    d.ellipse((235,490,485,770),fill=(151,103,66),outline=(94,62,45),width=7)
    d.ellipse((215,455,305,545),fill=(151,103,66),outline=(94,62,45),width=6); d.ellipse((400,455,490,545),fill=(151,103,66),outline=(94,62,45),width=6)
    d.ellipse((235,480,465,700),fill=(190,139,94))
    d.ellipse((285,560,305,585),fill=(35,35,45)); d.ellipse((395,560,415,585),fill=(35,35,45))
    d.ellipse((320,610,390,655),fill=(245,190,160)); d.ellipse((345,620,365,638),fill=(45,45,50))
    d.arc((315,625,390,685),0,180,fill=(70,45,40),width=5)
    # decorative flowers
    for x,y in [(100,850),(600,900),(160,1030),(540,1080)]:
        d.line((x,y,x,y+60),fill=(40,120,60),width=7)
        d.ellipse((x-18,y-18,x+18,y+18),fill=(255,120,165)); d.ellipse((x-8,y-8,x+8,y+8),fill=(255,220,70))
    centered(d,title,65,font(42), (255,255,255))
    centered(d,caption,900,font(30,False),(255,255,255),620)
    centered(d,"A tiny story with a big heart!",1160,font(22,False),(255,255,255),660)
    im.save(path)

def run(cmd): subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

def main():
    story=STORIES[(int(os.environ.get('GITHUB_RUN_NUMBER','1'))-1)%len(STORIES)]
    scenes=[]
    for i,line in enumerate(story['lines']):
        p=OUT/f"scene{i+1}.png"; scene(p,story['title'],line,i); scenes.append(p)
    text=' '.join(story['lines'])+' '+story['lesson']
    voice=OUT/'voice.wav'
    run(['espeak-ng','-v','en-us','-s','145','-w',str(voice),text])
    # Create a 3-scene vertical short. Each still is 10 seconds; narration plays over it.
    cmd=['ffmpeg','-y']
    for p in scenes: cmd += ['-loop','1','-t','10','-i',str(p)]
    cmd += ['-i',str(voice),'-filter_complex',
            '[0:v]scale=720:1280,setsar=1[v0];[1:v]scale=720:1280,setsar=1[v1];[2:v]scale=720:1280,setsar=1[v2];[v0][v1][v2]concat=n=3:v=1:a=0,format=yuv420p[v]',
            '-map','[v]','-map','3:a','-shortest','-c:v','libx264','-preset','ultrafast','-r','24','-c:a','aac','-b:a','128k','-movflags','+faststart',str(OUT/'kids_short.mp4')]
    run(cmd)
    metadata={'title':story['title']+' | Cute Kids Story #Shorts','description':story['lesson']+'\n\nA short, original story for children. #KidsStories #Shorts #BedtimeStory','tags':['kids story','children story','short story','kindness','shorts'],'made_for_kids':True}
    (OUT/'metadata.json').write_text(json.dumps(metadata,indent=2),encoding='utf-8')
    print(f"Generated {OUT/'kids_short.mp4'}")

if __name__=='__main__': main()
