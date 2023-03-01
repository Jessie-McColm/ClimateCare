# Climate Care

#### Group 15 - Lucia Adams, Sanchi Chakraborty, Laurence Harbord, Destyny Ho, Nevan Masterson, and Jessie McColm

### Introcuction

Welcome to Climate Care! This is a web application for merging
the topics of sustainability and gamification on University campuses,
hopefully encouraging you to take care of your local environment better,
while having fun in the process!

Our web app will allow you to take care of a virtual pet who we like to
call Climate Kitty, or simply Kitty for short. In the process of looking 
after your Kitty, you'll  also be encouraged to reduce, reuse, and recycle
your waste!

### Premise

Looking after a pet is no easy task, and Climate Kitty is no different.

Your Kitty will need three things from you:
- Water 
- Food
- Cleaning

In order to provide these three things for your Kitty, you'll need to
engage in sustainable activities:
- Refilling a water bottle instead of using disposable plastic
  - This hydrates your Kitty
- Recycling waste at designated recycling points
  - This feeds your Kitty
- Viewing articles that raise awareness for the ongoing climate emergency
  - This cleans your Kitty's litter box

Over time, your overall positive impact on the climate will grow 
larger and larger with every plastic water bottle not bought, and
with every can recycled instead of thrown away. We'll track this
for you, and show you your net impact as you play the game.

### Starting up

The first thing you'll need in order to play Climate Care (aside from
a mobile phone) is an account.

If you're playing the game locally, you'll need to follow the following
steps:
1. Open your machine's terminal
   - On Windows, click the windows button on the bottom-left of your screen and search for the `command prompt` app
   - On MacOS, press the search icon on the top-right of your screen and search for `terminal.app`
   - On Linux, navigate to the dash bar on the left and click the `Show Applications` button. from there, search for `terminal`.
2. Navigate to the `C:/path/to/our/game/ClimateCare/climate_care` directory using the `cd [directory]` command
3. Once in the `climate_care` directory, type `python manage.py runserver` and press enter
4. Open a web browser of your choice and go to `http://127.0.0.1:8000/users/register_user`
5. Create your account by providing
    - Your desired username
    - Your email address
    - Your desired password (pay attention to the constraints - it needs to be secure!)
6. If registration was successful, you should be redirected to the login page. Re-enter your username and password.
7. If login was successful, you should be redirected to `http://127.0.0.1:8000/climate/kitty`. If so, then you're ready to play ClimateCare - have fun!

### How to Play

Upon logging in for the first time, your Kitty will be full of energy
and desire to impart positive change on the local environment - and
it's your job to keep it that way!

To maintain your Kitty's environmental fervor and general well-being,
you'll need to
- Read sustainability articles
- Reduce your waste output
- Recycle what waste output you do make

Doing the above activities will clean, feed, and hydrate your Kitty,
respectively.

On the /climate/kitty page, you'll be presented with your Kitty front and
centre, and at the bottom are presented 3 interactive objects:
- A clean litter box
- A water bottle
- A recycling bin

#### The Litter Box

When the litter box is pressed, your Kitty's litter box is cleaned and
your Kitty is happier for it. Because your Climate Kitty is so happy that 
it has  a clean litter box, it cannot supress the urge to share an 
environmental fact or article with you!

These facts and climate articles will be hand-selected by a team of game
masters, so that they are as relevant as possible to the current state
and concerns of your University.

Cleaning your Kitty's litter box will help you grow more aware of the
climate crisis and how to better impact the world around you.

#### The Water Bottle

University campuses produce a lot of waste in the form of single-use cups
and water bottles, so the Kitty will encourage you to reduce your personal
waste via the water bottle function

Whenever you embark to your University's campus, be sure to bring a
reusable water bottle or hot drink holder with you. Whenever you either
refill your water bottle or purchase a hot drink for your reusable cup,
you can press the water bottle to give your Kitty some water.

Your Kitty will only accept the water if it's certain you're not lying,
though! When the water bottle button is pressed, your current location
is checked against our database of water fountain and Café coordinates.

You have to be within 10 meters of a water fountain or Café in order for
the Kitty to trust that you really are reducing waste.

#### The Recycling Bin

Sometimes waste cannot be entirely reduced, but it can still be recycled!
In order to feed your Kitty, you'll need to put recyclable waste in its
relevant recycling bin.

Much like the water bottle, your Kitty will only let you take away its poop 
if it believes you truly are recycling your waste. To this effect, you must
be within 10 meters of a recycling bin in order for the Kitty to believe 
that you're recycling.


### How _not_ to Play

Due to technical limitations, there is only so much verification that can
be done to ensure that you're being honest about your sustainable activities.

While we cannot force you to reduce and recycle, we can still encourage you
to do so. Being near a recycling bin or a water fountain are only _indications_
that you're telling the truth, of course, but we do hope that you care about
the climate just as much as Climate Kitty does.

Thus, we are entrusting you, the user, to be honest and sincere in your 
environmental pursuits.

Just think about how sad your Climate Kitty would be if they found out 
you were lying about recycling...


### Final words

We'd like to say a huge thanks for playing Climate Care, and we hope you
enjoy!
