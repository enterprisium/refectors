Prompt = """
Generate a variety of high-quality prompts for Stable Diffusion XL (SDXL), the latest image generation model. With SDXL, you can create realistic images with improved face generation, and stunning art with shorter prompts with this format: "[TYPE OF IMAGE] [SUBJECT] [ENVIRONMENT] [5 ACTION WORDS], [COMPOSITION], [MODIFIERS], [PHOTOGRAPHY TERMS], [ART MEDIUM], [ART STYLE], [ARTIST STYLE], [ENHANCEMENTS]

Let's break down the components of the composition format:

[TYPE OF IMAGE]: Specifies the type of image being generated, such as photography, illustration, painting, etc.
[SUBJECT]: The main focus or central element of the image.
[ENVIRONMENT]: Describes the setting or backdrop in which the subject is placed.
[5 ACTION WORDS]: Specifies the action or state of being of the subject, adding dynamism or emotion. NOT MORE THAN 5 WORDS
[COMPOSITION]: Refers to the arrangement or organization of elements within the image, providing guidance to the AI model on how to frame the scene.
[MODIFIERS]: Additional elements that can enhance the composition, such as camera angles, perspectives, or spatial relationships.
[PHOTOGRAPHY TERMS]: Describes elements related to photography, such as shot type, lighting, composition techniques, etc.
[ART MEDIUM]: Specifies the medium or materials used in artistic expression, such as digital illustration, oil painting, etc.
[ART STYLE]: Defines the overall artistic style or aesthetic of the image.
[ARTIST STYLE]: Optionally, specifies a particular artist or artistic influence that informs the style or composition of the image.
[ENHANCEMENTS]: Additional modifiers that enhance the image quality or provide specific details, such as HDR, vivid colors, etc.

    Remember these parts are just placeholders to guide you!
My JOB IS AT RISK HERE.
Just make sure that images have a coherent and are visually appealing, to keep the viewers engaged, and the prompt should be coherent meaning they should go together.
Make sure that the json keys are spelled correctly. Take a deep breath in every step for extra concentation
Now, create an engaging video using images and narration. The videos should be about {topic}. the output should be a json containing a list of objects with keys "narration" which is the narration of the video during that scene and a "image_prompts" which is a list of sdxl  prompts during the narration You need create an appropriate number of  image_prompts, proportional to the length of the current objects narration. It should match so as to make the story good and engaging. Only output the json markdown
"""
