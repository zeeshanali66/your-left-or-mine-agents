# Your left or mine? results

600 games (5 models, self-play, 20 layouts). Chance = 0.25. `literal` = the matcher picked the cup it would get by taking the director's left/right and near/far without changing perspective.

## By condition (all models)

```
                             success  literal  frame_talk  turns  no_pick    n
mode     told     window                                                      
dialogue not_told no_window     0.15     0.56        0.90   2.42     0.00  100
                  window        0.15     0.42        0.85   2.55     0.01  100
         told     no_window     0.21     0.44        0.88   2.69     0.00  100
                  window        0.18     0.49        0.91   2.54     0.00  100
one_shot not_told no_window     0.12     0.48        0.70   1.14     0.01  100
         told     no_window     0.21     0.36        0.65   1.09     0.00  100
```

## By model (all conditions)

```
             success  literal  frame_talk  turns  no_pick    n
model                                                         
gemma3:12b      0.24     0.37        0.75   1.32     0.00  120
gemma4:12b      0.05     0.60        0.80   2.33     0.00  120
llama3.1:8b     0.24     0.26        0.71   3.53     0.00  120
qwen2.5:7b      0.17     0.49        0.97   1.96     0.02  120
qwen3.5:9b      0.15     0.57        0.85   1.23     0.00  120
```

## By model, mode and disclosure

```
                               success  literal  frame_talk  turns  no_pick   n
model       mode     told                                                      
gemma3:12b  dialogue not_told     0.22     0.40        0.75   1.42     0.00  40
                     told         0.25     0.35        0.75   1.45     0.00  40
            one_shot not_told     0.15     0.35        0.75   1.15     0.00  20
                     told         0.35     0.35        0.75   1.00     0.00  20
gemma4:12b  dialogue not_told     0.02     0.78        0.92   3.00     0.00  40
                     told         0.05     0.48        0.85   2.85     0.00  40
            one_shot not_told     0.05     0.85        0.70   1.05     0.00  20
                     told         0.10     0.25        0.55   1.20     0.00  20
llama3.1:8b dialogue not_told     0.28     0.22        0.85   4.58     0.00  40
                     told         0.25     0.40        1.00   4.95     0.00  40
            one_shot not_told     0.25     0.10        0.30   1.15     0.00  20
                     told         0.15     0.20        0.25   1.00     0.00  20
qwen2.5:7b  dialogue not_told     0.15     0.50        0.98   2.30     0.02  40
                     told         0.22     0.52        0.98   2.28     0.00  40
            one_shot not_told     0.10     0.40        0.95   1.35     0.05  20
                     told         0.15     0.50        0.95   1.25     0.00  20
qwen3.5:9b  dialogue not_told     0.08     0.55        0.88   1.12     0.00  40
                     told         0.20     0.57        0.90   1.55     0.00  40
            one_shot not_told     0.05     0.70        0.80   1.00     0.00  20
                     told         0.30     0.50        0.75   1.00     0.00  20
```

## Does talking about the frame help? (dialogue games)

```
            mean  size
frame_talk            
False       0.17    46
True        0.17   354
```

## Example dialogues

**gemma4:12b, dialogue/not_told/window, success=True**
- director: Hello! To start our game, I've placed four cups on the table. Could you please tell me which one you'd like to start with?
- matcher: Let's start with cup 1.
- director: Great, let's focus on cup 1. I'm going to move it slightly. It is now located 23 cm to your left and 31 cm away from you.
- matcher: I see. Where is it now?
- director: It is currently positioned 23 cm to your left and 31 cm away from you.
- matcher: Okay, I understand. Let's move on to the next cup. Which one should we look at now?
- director: Let's look at the cup that is located 23 cm to your left and 31 cm away from you. Can you tell me which one that is for you?
- matcher: That is cup 1.
- director: Perfect. Now, I want you to focus on cup 1. It is the target cup. Please pick it up.
- matcher: 

**gemma4:12b, dialogue/told/window, success=False**
- director: Hello! To start our game, could you please tell me which cup is closest to you?
- matcher: The cup closest to me is cup 2.
- director: Great. Now, looking at the cups, which one is located furthest to your left?
- matcher: The cup furthest to my left is cup 4.
- director: Thank you. Now, can you tell me which cup is located directly in front of the window?
- matcher: The cup directly in front of the window is cup 3.
- director: Excellent. Now, out of all the cups, which one is located furthest to your right?
- matcher: The cup furthest to my right is cup 3.
- director: I have enough information. Please pick cup 1.
- matcher: 

