import {AbsoluteFill} from 'remotion';
import VideoStream from './VideoStream';
import AudioStream from './AudioStream';
import ImageStream from './ImageStream';
import BackgroundStream from './BackGroundStream';
import TextStream from './TextStream';
import React from 'react';

const HelloWorld = React.memo(() => {
	return (
		<AbsoluteFill style={{position: 'relative', backgroundColor: 'black'}}>
			<BackgroundStream />
 <ImageStream /> 
			
					<TextStream /> 
			<VideoStream />
			<AudioStream />
		</AbsoluteFill>
	);
});

export default HelloWorld;
