// All configuration options: https://remotion.dev/docs/config
// Each option also is available as a CLI flag: https://remotion.dev/docs/cli

// Note: When using the Node.JS APIs, the config file doesn't apply. Instead, pass options directly to the APIs

import {Config} from '@remotion/cli/config';
import Instructions from './ServerInstructions.json';
import {enableTailwind} from '@remotion/tailwind';
Config.overrideWebpackConfig((currentConfiguration) => {
	return enableTailwind(currentConfiguration);
});

//Config.setBrowserExecutable("/usr/bin/chrome-headless-shell");
Config.setVideoImageFormat('jpeg');
Config.setConcurrency(1);
