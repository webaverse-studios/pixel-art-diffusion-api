from pixel_art_diffusion import generate as generate

prompt = "giant monster forest background"
seed = 42
steps = 1000 # Steps: [25,50,100,150,250,500,1000]

input_prompt = "#pixelart, #16bit, " + prompt

generate(input_prompt=input_prompt, input_steps=steps, input_seed=seed)