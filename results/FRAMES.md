# Frame analysis

## Success by the frame the director used

```
                  success  literal    n
frame                                  
both                 0.12     0.44   43
no left/right        0.21     0.27  143
right frame only     0.28     0.33  198
wrong frame only     0.05     0.70  216
```

## Frame use by model

```
frame        both  no left/right  right frame only  wrong frame only
model                                                               
gemma3:12b   0.07           0.33              0.38              0.22
gemma4:12b   0.08           0.25              0.27              0.41
llama3.1:8b  0.13           0.42              0.40              0.05
qwen2.5:7b   0.03           0.04              0.19              0.73
qwen3.5:9b   0.05           0.15              0.41              0.39
```

## Frame use by disclosure (told the partner sits opposite?)

```
frame              both  no left/right  right frame only  wrong frame only
mode     told                                                             
dialogue not_told  0.08           0.19              0.29              0.44
         told      0.13           0.16              0.41              0.30
one_shot not_told  0.01           0.35              0.24              0.40
         told      0.01           0.38              0.34              0.27
```

## Perspective words (facing, opposite, from my side, mirror, ...)

```
told
not_told    0.02
told        0.07

                   mean  size
perspective_words            
False              0.17   575
True               0.08    25
```

## Director names its own private cup labels (A-D), which the partner cannot know

```
model
gemma3:12b     0.07
gemma4:12b     0.00
llama3.1:8b    0.42
qwen2.5:7b     0.52
qwen3.5:9b     0.00

                          mean  size
director_uses_own_labels            
False                     0.15   479
True                      0.25   121
```
