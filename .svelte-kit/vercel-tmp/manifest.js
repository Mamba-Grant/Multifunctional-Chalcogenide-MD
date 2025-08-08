export const manifest = (() => {
function __memo(fn) {
	let value;
	return () => value ??= (value = fn());
}

return {
	appDir: "_app",
	appPath: "_app",
	assets: new Set(["favicon.svg"]),
	mimeTypes: {".svg":"image/svg+xml"},
	_: {
		client: {start:"_app/immutable/entry/start.DtaS4cJj.js",app:"_app/immutable/entry/app.BvTYRYdq.js",imports:["_app/immutable/entry/start.DtaS4cJj.js","_app/immutable/chunks/tyFR4mit.js","_app/immutable/chunks/D9wKpdpy.js","_app/immutable/chunks/Dh2_OmFi.js","_app/immutable/entry/app.BvTYRYdq.js","_app/immutable/chunks/Dh2_OmFi.js","_app/immutable/chunks/D9wKpdpy.js","_app/immutable/chunks/DsnmJJEf.js","_app/immutable/chunks/B1VSs12J.js"],stylesheets:[],fonts:[],uses_env_dynamic_public:false},
		nodes: [
			__memo(() => import('../output/server/nodes/0.js')),
			__memo(() => import('../output/server/nodes/1.js')),
			__memo(() => import('../output/server/nodes/2.js'))
		],
		remotes: {
			
		},
		routes: [
			{
				id: "/",
				pattern: /^\/$/,
				params: [],
				page: { layouts: [0,], errors: [1,], leaf: 2 },
				endpoint: null
			}
		],
		prerendered_routes: new Set([]),
		matchers: async () => {
			
			return {  };
		},
		server_assets: {}
	}
}
})();
