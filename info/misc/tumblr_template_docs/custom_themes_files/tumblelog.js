function flashVersion(){if(navigator.plugins&&navigator.plugins.length>0){var a=navigator.mimeTypes;if(a&&a['application/x-shockwave-flash']&&a['application/x-shockwave-flash'].enabledPlugin&&a['application/x-shockwave-flash'].enabledPlugin.description){return parseInt(a['application/x-shockwave-flash'].enabledPlugin.description.split(' ')[2].split('.')[0],10)}}else if(navigator.appVersion.indexOf("Mac")==-1&&window.execScript){try{var b=new ActiveXObject("ShockwaveFlash.ShockwaveFlash.7");var c=b.GetVariable("$version");return c.split(',')[0].split(' ')[1]}catch(e){}return 0}}function replaceIfFlash9(a,b){if(flashVersion()>=9)document.getElementById(a).innerHTML=b}