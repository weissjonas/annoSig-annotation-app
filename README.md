# anno5i9
annotation game for signals, mainly fECG


# motivation

My dearest Fellows, 

As you may know, I'm writing my PhD about fetal ECG. This method comes with high noise, which makes it necessary to select usable data.  Usually, the problem is tackled by a few trained scientists who spend long boring hours in front of a bad user interface. I'm lazy and sure not keen on doing this. So I thought about how to avoid this. Maybe a bunch of children could do the boring work for me - and have fun with is. =)  So let's create a game to annotate signals, that is fun and give us a lot more data that we ever need.

Best, Jonas


# goal
Program for grouping data into several categories according to their signal-to-noise ratio. The game should appeal to a target group of 8 years and older. If possible, motivate them to keep playing for some time.

As a second step, it would be conceivable to annotate events (fQRS).

### The signal quality of signals should be divided into 4 categories:
 - very good
 - good
 - Signal just still visible
 - no useful signal


# Data representation

## Visual
 - plot
 - 1D parameter e.g. a lamp

### Time series
Advantage:
- Morphology well recognizable

Disadvantage:
- technical

How many seconds can be displayed?

### Fourier transformation
Possibly more can be seen over the frequency space than in time series. Possibly as supporting criterion (e.g. relative power in the range 0.3..0.8 Hz is displayed as a lamp -> the brighter the better).

### Wavelet transformation
Better than Fourier?

## Sounds
Could work well, but may be annoying.

### Possibilities:
- Play signal at increased speed so that periodic signals are audible.

### Advantage:
 - a lot of signal in a short time


# Reward system

## General motivational opportunities
 - Money (microtransactions)
 - social recognition (post on facebook!)
 - Praise (*"Thank you! (for helping us save babies)"*)
 - Badges
 - growing (Tamagotchi, Pokemon)

## problem ground truth
The truth is not known for all data.
This makes it hard for in-game motivation techniques to work.
We could think of a way to suggest the player that we know if the answer is correct or not, but this comes with some downsides.

I would propose that we first build the interface, test it and then think of a way how the player may have a good time while playing.


# Game principle

## Simple Thank You Game

The game praises you for your good nature. Parallel shows beautiful pictures and offers the possibility to earn badges, which can be posted on social media.
It explains in detail what the data is used for and how it benefits research and society.

This would do the trick for the beginning.

## Pokemon

At the beginning of the game, you get a creature.
You can feed it during the game and play with it.
This costs an in-game currency, which can be unlocked via annotations.
The creature can develop, but after a certain time, it is hungry and loses confidence in the player.
So you have to play again.

### Problem
The player is motivated to farm the currency, not to annotate correctly.

## Adventure Capitalist

Farming gives you raw materials that you can use to automate the farming of a resource and build a larger machine that you can use to farm a new resource. etc.

### Problem
The player is motivated to farm the currency, not to annotate correctly.
