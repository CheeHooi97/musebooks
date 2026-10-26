const base = "file:///D:/Workspace/Go/musebooks/frontend/node_modules/@fontsource";
export const fontCSS = `
@font-face { font-family: Gloock; src: url(${base}/gloock/files/gloock-latin-400-normal.woff2); }
@font-face { font-family: Hanken; font-weight: 400; src: url(${base}/hanken-grotesk/files/hanken-grotesk-latin-400-normal.woff2); }
@font-face { font-family: Hanken; font-weight: 500; src: url(${base}/hanken-grotesk/files/hanken-grotesk-latin-500-normal.woff2); }
@font-face { font-family: Hanken; font-weight: 600; src: url(${base}/hanken-grotesk/files/hanken-grotesk-latin-600-normal.woff2); }
@font-face { font-family: Hanken; font-weight: 700; src: url(${base}/hanken-grotesk/files/hanken-grotesk-latin-700-normal.woff2); }
@font-face { font-family: Hanken; font-weight: 800; src: url(${base}/hanken-grotesk/files/hanken-grotesk-latin-800-normal.woff2); }
@font-face { font-family: Azeret; font-weight: 500; src: url(${base}/azeret-mono/files/azeret-mono-latin-500-normal.woff2); }
*{box-sizing:border-box;margin:0} body{-webkit-font-smoothing:antialiased}`;
const bodoni = "file:///D:/Workspace/Go/musebooks/brand/node_modules/@fontsource/bodoni-moda/files";
export const luxeFontCSS = `${fontCSS}
@font-face { font-family: Bodoni; font-weight: 400; src: url(${bodoni}/bodoni-moda-latin-400-normal.woff2); }
@font-face { font-family: Bodoni; font-weight: 500; src: url(${bodoni}/bodoni-moda-latin-500-normal.woff2); }`;
