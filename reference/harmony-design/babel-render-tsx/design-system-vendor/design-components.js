import * as e from "react";
import t, { createContext as n, createElement as r, forwardRef as i, useCallback as a, useContext as o, useEffect as s, useId as c, useMemo as l, useRef as u, useState as d } from "react";
import * as f from "react-dom/client";
import { Fragment as p, jsx as m, jsxs as h } from "react/jsx-runtime";
//#region \0rolldown/runtime.js
var g = Object.defineProperty, _ = (e, t) => {
	let n = {};
	for (var r in e) g(n, r, {
		get: e[r],
		enumerable: !0
	});
	return t || g(n, Symbol.toStringTag, { value: "Module" }), n;
};
//#endregion
//#region node_modules/.pnpm/clsx@2.1.1/node_modules/clsx/dist/clsx.mjs
function v(e) {
	var t, n, r = "";
	if (typeof e == "string" || typeof e == "number") r += e;
	else if (typeof e == "object") if (Array.isArray(e)) {
		var i = e.length;
		for (t = 0; t < i; t++) e[t] && (n = v(e[t])) && (r && (r += " "), r += n);
	} else for (n in e) e[n] && (r && (r += " "), r += n);
	return r;
}
function y() {
	for (var e, t, n = 0, r = "", i = arguments.length; n < i; n++) (e = arguments[n]) && (t = v(e)) && (r && (r += " "), r += t);
	return r;
}
//#endregion
//#region node_modules/.pnpm/tailwind-merge@3.6.0/node_modules/tailwind-merge/dist/bundle-mjs.mjs
var b = (e, t) => {
	let n = Array(e.length + t.length);
	for (let t = 0; t < e.length; t++) n[t] = e[t];
	for (let r = 0; r < t.length; r++) n[e.length + r] = t[r];
	return n;
}, x = (e, t) => ({
	classGroupId: e,
	validator: t
}), S = (e = /* @__PURE__ */ new Map(), t = null, n) => ({
	nextPart: e,
	validators: t,
	classGroupId: n
}), C = "-", w = [], T = "arbitrary..", E = (e) => {
	let t = k(e), { conflictingClassGroups: n, conflictingClassGroupModifiers: r } = e;
	return {
		getClassGroupId: (e) => {
			if (e.startsWith("[") && e.endsWith("]")) return O(e);
			let n = e.split(C);
			return D(n, +(n[0] === "" && n.length > 1), t);
		},
		getConflictingClassGroupIds: (e, t) => {
			if (t) {
				let t = r[e], i = n[e];
				return t ? i ? b(i, t) : t : i || w;
			}
			return n[e] || w;
		}
	};
}, D = (e, t, n) => {
	if (e.length - t === 0) return n.classGroupId;
	let r = e[t], i = n.nextPart.get(r);
	if (i) {
		let n = D(e, t + 1, i);
		if (n) return n;
	}
	let a = n.validators;
	if (a === null) return;
	let o = t === 0 ? e.join(C) : e.slice(t).join(C), s = a.length;
	for (let e = 0; e < s; e++) {
		let t = a[e];
		if (t.validator(o)) return t.classGroupId;
	}
}, O = (e) => e.slice(1, -1).indexOf(":") === -1 ? void 0 : (() => {
	let t = e.slice(1, -1), n = t.indexOf(":"), r = t.slice(0, n);
	return r ? T + r : void 0;
})(), k = (e) => {
	let { theme: t, classGroups: n } = e;
	return A(n, t);
}, A = (e, t) => {
	let n = S();
	for (let r in e) {
		let i = e[r];
		j(i, n, r, t);
	}
	return n;
}, j = (e, t, n, r) => {
	let i = e.length;
	for (let a = 0; a < i; a++) {
		let i = e[a];
		M(i, t, n, r);
	}
}, M = (e, t, n, r) => {
	if (typeof e == "string") {
		N(e, t, n);
		return;
	}
	if (typeof e == "function") {
		P(e, t, n, r);
		return;
	}
	F(e, t, n, r);
}, N = (e, t, n) => {
	let r = e === "" ? t : I(t, e);
	r.classGroupId = n;
}, P = (e, t, n, r) => {
	if (L(e)) {
		j(e(r), t, n, r);
		return;
	}
	t.validators === null && (t.validators = []), t.validators.push(x(n, e));
}, F = (e, t, n, r) => {
	let i = Object.entries(e), a = i.length;
	for (let e = 0; e < a; e++) {
		let [a, o] = i[e];
		j(o, I(t, a), n, r);
	}
}, I = (e, t) => {
	let n = e, r = t.split(C), i = r.length;
	for (let e = 0; e < i; e++) {
		let t = r[e], i = n.nextPart.get(t);
		i || (i = S(), n.nextPart.set(t, i)), n = i;
	}
	return n;
}, L = (e) => "isThemeGetter" in e && e.isThemeGetter === !0, R = (e) => {
	if (e < 1) return {
		get: () => void 0,
		set: () => {}
	};
	let t = 0, n = Object.create(null), r = Object.create(null), i = (i, a) => {
		n[i] = a, t++, t > e && (t = 0, r = n, n = Object.create(null));
	};
	return {
		get(e) {
			let t = n[e];
			if (t !== void 0) return t;
			if ((t = r[e]) !== void 0) return i(e, t), t;
		},
		set(e, t) {
			e in n ? n[e] = t : i(e, t);
		}
	};
}, z = "!", B = ":", V = [], H = (e, t, n, r, i) => ({
	modifiers: e,
	hasImportantModifier: t,
	baseClassName: n,
	maybePostfixModifierPosition: r,
	isExternal: i
}), ee = (e) => {
	let { prefix: t, experimentalParseClassName: n } = e, r = (e) => {
		let t = [], n = 0, r = 0, i = 0, a, o = e.length;
		for (let s = 0; s < o; s++) {
			let o = e[s];
			if (n === 0 && r === 0) {
				if (o === B) {
					t.push(e.slice(i, s)), i = s + 1;
					continue;
				}
				if (o === "/") {
					a = s;
					continue;
				}
			}
			o === "[" ? n++ : o === "]" ? n-- : o === "(" ? r++ : o === ")" && r--;
		}
		let s = t.length === 0 ? e : e.slice(i), c = s, l = !1;
		s.endsWith(z) ? (c = s.slice(0, -1), l = !0) : s.startsWith(z) && (c = s.slice(1), l = !0);
		let u = a && a > i ? a - i : void 0;
		return H(t, l, c, u);
	};
	if (t) {
		let e = t + B, n = r;
		r = (t) => t.startsWith(e) ? n(t.slice(e.length)) : H(V, !1, t, void 0, !0);
	}
	if (n) {
		let e = r;
		r = (t) => n({
			className: t,
			parseClassName: e
		});
	}
	return r;
}, te = (e) => {
	let t = /* @__PURE__ */ new Map();
	return e.orderSensitiveModifiers.forEach((e, n) => {
		t.set(e, 1e6 + n);
	}), (e) => {
		let n = [], r = [];
		for (let i = 0; i < e.length; i++) {
			let a = e[i], o = a[0] === "[", s = t.has(a);
			o || s ? (r.length > 0 && (r.sort(), n.push(...r), r = []), n.push(a)) : r.push(a);
		}
		return r.length > 0 && (r.sort(), n.push(...r)), n;
	};
}, U = (e) => ({
	cache: R(e.cacheSize),
	parseClassName: ee(e),
	sortModifiers: te(e),
	postfixLookupClassGroupIds: ne(e),
	...E(e)
}), ne = (e) => {
	let t = Object.create(null), n = e.postfixLookupClassGroups;
	if (n) for (let e = 0; e < n.length; e++) t[n[e]] = !0;
	return t;
}, re = /\s+/, ie = (e, t) => {
	let { parseClassName: n, getClassGroupId: r, getConflictingClassGroupIds: i, sortModifiers: a, postfixLookupClassGroupIds: o } = t, s = [], c = e.trim().split(re), l = "";
	for (let e = c.length - 1; e >= 0; --e) {
		let t = c[e], { isExternal: u, modifiers: d, hasImportantModifier: f, baseClassName: p, maybePostfixModifierPosition: m } = n(t);
		if (u) {
			l = t + (l.length > 0 ? " " + l : l);
			continue;
		}
		let h = !!m, g;
		if (h) {
			g = r(p.substring(0, m));
			let e = g && o[g] ? r(p) : void 0;
			e && e !== g && (g = e, h = !1);
		} else g = r(p);
		if (!g) {
			if (!h) {
				l = t + (l.length > 0 ? " " + l : l);
				continue;
			}
			if (g = r(p), !g) {
				l = t + (l.length > 0 ? " " + l : l);
				continue;
			}
			h = !1;
		}
		let _ = d.length === 0 ? "" : d.length === 1 ? d[0] : a(d).join(":"), v = f ? _ + z : _, y = v + g;
		if (s.indexOf(y) > -1) continue;
		s.push(y);
		let b = i(g, h);
		for (let e = 0; e < b.length; ++e) {
			let t = b[e];
			s.push(v + t);
		}
		l = t + (l.length > 0 ? " " + l : l);
	}
	return l;
}, ae = (...e) => {
	let t = 0, n, r, i = "";
	for (; t < e.length;) (n = e[t++]) && (r = oe(n)) && (i && (i += " "), i += r);
	return i;
}, oe = (e) => {
	if (typeof e == "string") return e;
	let t, n = "";
	for (let r = 0; r < e.length; r++) e[r] && (t = oe(e[r])) && (n && (n += " "), n += t);
	return n;
}, se = (e, ...t) => {
	let n, r, i, a, o = (o) => (n = U(t.reduce((e, t) => t(e), e())), r = n.cache.get, i = n.cache.set, a = s, s(o)), s = (e) => {
		let t = r(e);
		if (t) return t;
		let a = ie(e, n);
		return i(e, a), a;
	};
	return a = o, (...e) => a(ae(...e));
}, ce = [], W = (e) => {
	let t = (t) => t[e] || ce;
	return t.isThemeGetter = !0, t;
}, le = /^\[(?:(\w[\w-]*):)?(.+)\]$/i, ue = /^\((?:(\w[\w-]*):)?(.+)\)$/i, de = /^\d+(?:\.\d+)?\/\d+(?:\.\d+)?$/, fe = /^(\d+(\.\d+)?)?(xs|sm|md|lg|xl)$/, pe = /\d+(%|px|r?em|[sdl]?v([hwib]|min|max)|pt|pc|in|cm|mm|cap|ch|ex|r?lh|cq(w|h|i|b|min|max))|\b(calc|min|max|clamp)\(.+\)|^0$/, me = /^(rgba?|hsla?|hwb|(ok)?(lab|lch)|color-mix)\(.+\)$/, he = /^(inset_)?-?((\d+)?\.?(\d+)[a-z]+|0)_-?((\d+)?\.?(\d+)[a-z]+|0)/, ge = /^(url|image|image-set|cross-fade|element|(repeating-)?(linear|radial|conic)-gradient)\(.+\)$/, _e = (e) => de.test(e), G = (e) => !!e && !Number.isNaN(Number(e)), K = (e) => !!e && Number.isInteger(Number(e)), ve = (e) => e.endsWith("%") && G(e.slice(0, -1)), q = (e) => fe.test(e), ye = () => !0, be = (e) => pe.test(e) && !me.test(e), xe = () => !1, Se = (e) => he.test(e), Ce = (e) => ge.test(e), we = (e) => !J(e) && !Y(e), Te = (e) => e.startsWith("@container") && (e[10] === "/" && e[11] !== void 0 || e[11] === "s" && e[16] !== void 0 && e.startsWith("-size/", 10) || e[11] === "n" && e[18] !== void 0 && e.startsWith("-normal/", 10)), Ee = (e) => Ve(e, Ge, xe), J = (e) => le.test(e), De = (e) => Ve(e, Ke, be), Oe = (e) => Ve(e, qe, G), ke = (e) => Ve(e, Ye, ye), Ae = (e) => Ve(e, Je, xe), je = (e) => Ve(e, Ue, xe), Me = (e) => Ve(e, We, Ce), Ne = (e) => Ve(e, Xe, Se), Y = (e) => ue.test(e), Pe = (e) => He(e, Ke), Fe = (e) => He(e, Je), Ie = (e) => He(e, Ue), Le = (e) => He(e, Ge), Re = (e) => He(e, We), ze = (e) => He(e, Xe, !0), Be = (e) => He(e, Ye, !0), Ve = (e, t, n) => {
	let r = le.exec(e);
	return r ? r[1] ? t(r[1]) : n(r[2]) : !1;
}, He = (e, t, n = !1) => {
	let r = ue.exec(e);
	return r ? r[1] ? t(r[1]) : n : !1;
}, Ue = (e) => e === "position" || e === "percentage", We = (e) => e === "image" || e === "url", Ge = (e) => e === "length" || e === "size" || e === "bg-size", Ke = (e) => e === "length", qe = (e) => e === "number", Je = (e) => e === "family-name", Ye = (e) => e === "number" || e === "weight", Xe = (e) => e === "shadow", Ze = /* @__PURE__ */ se(() => {
	let e = W("color"), t = W("font"), n = W("text"), r = W("font-weight"), i = W("tracking"), a = W("leading"), o = W("breakpoint"), s = W("container"), c = W("spacing"), l = W("radius"), u = W("shadow"), d = W("inset-shadow"), f = W("text-shadow"), p = W("drop-shadow"), m = W("blur"), h = W("perspective"), g = W("aspect"), _ = W("ease"), v = W("animate"), y = () => [
		"auto",
		"avoid",
		"all",
		"avoid-page",
		"page",
		"left",
		"right",
		"column"
	], b = () => [
		"center",
		"top",
		"bottom",
		"left",
		"right",
		"top-left",
		"left-top",
		"top-right",
		"right-top",
		"bottom-right",
		"right-bottom",
		"bottom-left",
		"left-bottom"
	], x = () => [
		...b(),
		Y,
		J
	], S = () => [
		"auto",
		"hidden",
		"clip",
		"visible",
		"scroll"
	], C = () => [
		"auto",
		"contain",
		"none"
	], w = () => [
		Y,
		J,
		c
	], T = () => [
		_e,
		"full",
		"auto",
		...w()
	], E = () => [
		K,
		"none",
		"subgrid",
		Y,
		J
	], D = () => [
		"auto",
		{ span: [
			"full",
			K,
			Y,
			J
		] },
		K,
		Y,
		J
	], O = () => [
		K,
		"auto",
		Y,
		J
	], k = () => [
		"auto",
		"min",
		"max",
		"fr",
		Y,
		J
	], A = () => [
		"start",
		"end",
		"center",
		"between",
		"around",
		"evenly",
		"stretch",
		"baseline",
		"center-safe",
		"end-safe"
	], j = () => [
		"start",
		"end",
		"center",
		"stretch",
		"center-safe",
		"end-safe"
	], M = () => ["auto", ...w()], N = () => [
		_e,
		"auto",
		"full",
		"dvw",
		"dvh",
		"lvw",
		"lvh",
		"svw",
		"svh",
		"min",
		"max",
		"fit",
		...w()
	], P = () => [
		_e,
		"screen",
		"full",
		"dvw",
		"lvw",
		"svw",
		"min",
		"max",
		"fit",
		...w()
	], F = () => [
		_e,
		"screen",
		"full",
		"lh",
		"dvh",
		"lvh",
		"svh",
		"min",
		"max",
		"fit",
		...w()
	], I = () => [
		e,
		Y,
		J
	], L = () => [
		...b(),
		Ie,
		je,
		{ position: [Y, J] }
	], R = () => ["no-repeat", { repeat: [
		"",
		"x",
		"y",
		"space",
		"round"
	] }], z = () => [
		"auto",
		"cover",
		"contain",
		Le,
		Ee,
		{ size: [Y, J] }
	], B = () => [
		ve,
		Pe,
		De
	], V = () => [
		"",
		"none",
		"full",
		l,
		Y,
		J
	], H = () => [
		"",
		G,
		Pe,
		De
	], ee = () => [
		"solid",
		"dashed",
		"dotted",
		"double"
	], te = () => [
		"normal",
		"multiply",
		"screen",
		"overlay",
		"darken",
		"lighten",
		"color-dodge",
		"color-burn",
		"hard-light",
		"soft-light",
		"difference",
		"exclusion",
		"hue",
		"saturation",
		"color",
		"luminosity"
	], U = () => [
		G,
		ve,
		Ie,
		je
	], ne = () => [
		"",
		"none",
		m,
		Y,
		J
	], re = () => [
		"none",
		G,
		Y,
		J
	], ie = () => [
		"none",
		G,
		Y,
		J
	], ae = () => [
		G,
		Y,
		J
	], oe = () => [
		_e,
		"full",
		...w()
	];
	return {
		cacheSize: 500,
		theme: {
			animate: [
				"spin",
				"ping",
				"pulse",
				"bounce"
			],
			aspect: ["video"],
			blur: [q],
			breakpoint: [q],
			color: [ye],
			container: [q],
			"drop-shadow": [q],
			ease: [
				"in",
				"out",
				"in-out"
			],
			font: [we],
			"font-weight": [
				"thin",
				"extralight",
				"light",
				"normal",
				"medium",
				"semibold",
				"bold",
				"extrabold",
				"black"
			],
			"inset-shadow": [q],
			leading: [
				"none",
				"tight",
				"snug",
				"normal",
				"relaxed",
				"loose"
			],
			perspective: [
				"dramatic",
				"near",
				"normal",
				"midrange",
				"distant",
				"none"
			],
			radius: [q],
			shadow: [q],
			spacing: ["px", G],
			text: [q],
			"text-shadow": [q],
			tracking: [
				"tighter",
				"tight",
				"normal",
				"wide",
				"wider",
				"widest"
			]
		},
		classGroups: {
			aspect: [{ aspect: [
				"auto",
				"square",
				_e,
				J,
				Y,
				g
			] }],
			container: ["container"],
			"container-type": [{ "@container": [
				"",
				"normal",
				"size",
				Y,
				J
			] }],
			"container-named": [Te],
			columns: [{ columns: [
				G,
				J,
				Y,
				s
			] }],
			"break-after": [{ "break-after": y() }],
			"break-before": [{ "break-before": y() }],
			"break-inside": [{ "break-inside": [
				"auto",
				"avoid",
				"avoid-page",
				"avoid-column"
			] }],
			"box-decoration": [{ "box-decoration": ["slice", "clone"] }],
			box: [{ box: ["border", "content"] }],
			display: [
				"block",
				"inline-block",
				"inline",
				"flex",
				"inline-flex",
				"table",
				"inline-table",
				"table-caption",
				"table-cell",
				"table-column",
				"table-column-group",
				"table-footer-group",
				"table-header-group",
				"table-row-group",
				"table-row",
				"flow-root",
				"grid",
				"inline-grid",
				"contents",
				"list-item",
				"hidden"
			],
			sr: ["sr-only", "not-sr-only"],
			float: [{ float: [
				"right",
				"left",
				"none",
				"start",
				"end"
			] }],
			clear: [{ clear: [
				"left",
				"right",
				"both",
				"none",
				"start",
				"end"
			] }],
			isolation: ["isolate", "isolation-auto"],
			"object-fit": [{ object: [
				"contain",
				"cover",
				"fill",
				"none",
				"scale-down"
			] }],
			"object-position": [{ object: x() }],
			overflow: [{ overflow: S() }],
			"overflow-x": [{ "overflow-x": S() }],
			"overflow-y": [{ "overflow-y": S() }],
			overscroll: [{ overscroll: C() }],
			"overscroll-x": [{ "overscroll-x": C() }],
			"overscroll-y": [{ "overscroll-y": C() }],
			position: [
				"static",
				"fixed",
				"absolute",
				"relative",
				"sticky"
			],
			inset: [{ inset: T() }],
			"inset-x": [{ "inset-x": T() }],
			"inset-y": [{ "inset-y": T() }],
			start: [{
				"inset-s": T(),
				start: T()
			}],
			end: [{
				"inset-e": T(),
				end: T()
			}],
			"inset-bs": [{ "inset-bs": T() }],
			"inset-be": [{ "inset-be": T() }],
			top: [{ top: T() }],
			right: [{ right: T() }],
			bottom: [{ bottom: T() }],
			left: [{ left: T() }],
			visibility: [
				"visible",
				"invisible",
				"collapse"
			],
			z: [{ z: [
				K,
				"auto",
				Y,
				J
			] }],
			basis: [{ basis: [
				_e,
				"full",
				"auto",
				s,
				...w()
			] }],
			"flex-direction": [{ flex: [
				"row",
				"row-reverse",
				"col",
				"col-reverse"
			] }],
			"flex-wrap": [{ flex: [
				"nowrap",
				"wrap",
				"wrap-reverse"
			] }],
			flex: [{ flex: [
				G,
				_e,
				"auto",
				"initial",
				"none",
				J
			] }],
			grow: [{ grow: [
				"",
				G,
				Y,
				J
			] }],
			shrink: [{ shrink: [
				"",
				G,
				Y,
				J
			] }],
			order: [{ order: [
				K,
				"first",
				"last",
				"none",
				Y,
				J
			] }],
			"grid-cols": [{ "grid-cols": E() }],
			"col-start-end": [{ col: D() }],
			"col-start": [{ "col-start": O() }],
			"col-end": [{ "col-end": O() }],
			"grid-rows": [{ "grid-rows": E() }],
			"row-start-end": [{ row: D() }],
			"row-start": [{ "row-start": O() }],
			"row-end": [{ "row-end": O() }],
			"grid-flow": [{ "grid-flow": [
				"row",
				"col",
				"dense",
				"row-dense",
				"col-dense"
			] }],
			"auto-cols": [{ "auto-cols": k() }],
			"auto-rows": [{ "auto-rows": k() }],
			gap: [{ gap: w() }],
			"gap-x": [{ "gap-x": w() }],
			"gap-y": [{ "gap-y": w() }],
			"justify-content": [{ justify: [...A(), "normal"] }],
			"justify-items": [{ "justify-items": [...j(), "normal"] }],
			"justify-self": [{ "justify-self": ["auto", ...j()] }],
			"align-content": [{ content: ["normal", ...A()] }],
			"align-items": [{ items: [...j(), { baseline: ["", "last"] }] }],
			"align-self": [{ self: [
				"auto",
				...j(),
				{ baseline: ["", "last"] }
			] }],
			"place-content": [{ "place-content": A() }],
			"place-items": [{ "place-items": [...j(), "baseline"] }],
			"place-self": [{ "place-self": ["auto", ...j()] }],
			p: [{ p: w() }],
			px: [{ px: w() }],
			py: [{ py: w() }],
			ps: [{ ps: w() }],
			pe: [{ pe: w() }],
			pbs: [{ pbs: w() }],
			pbe: [{ pbe: w() }],
			pt: [{ pt: w() }],
			pr: [{ pr: w() }],
			pb: [{ pb: w() }],
			pl: [{ pl: w() }],
			m: [{ m: M() }],
			mx: [{ mx: M() }],
			my: [{ my: M() }],
			ms: [{ ms: M() }],
			me: [{ me: M() }],
			mbs: [{ mbs: M() }],
			mbe: [{ mbe: M() }],
			mt: [{ mt: M() }],
			mr: [{ mr: M() }],
			mb: [{ mb: M() }],
			ml: [{ ml: M() }],
			"space-x": [{ "space-x": w() }],
			"space-x-reverse": ["space-x-reverse"],
			"space-y": [{ "space-y": w() }],
			"space-y-reverse": ["space-y-reverse"],
			size: [{ size: N() }],
			"inline-size": [{ inline: ["auto", ...P()] }],
			"min-inline-size": [{ "min-inline": ["auto", ...P()] }],
			"max-inline-size": [{ "max-inline": ["none", ...P()] }],
			"block-size": [{ block: ["auto", ...F()] }],
			"min-block-size": [{ "min-block": ["auto", ...F()] }],
			"max-block-size": [{ "max-block": ["none", ...F()] }],
			w: [{ w: [
				s,
				"screen",
				...N()
			] }],
			"min-w": [{ "min-w": [
				s,
				"screen",
				"none",
				...N()
			] }],
			"max-w": [{ "max-w": [
				s,
				"screen",
				"none",
				"prose",
				{ screen: [o] },
				...N()
			] }],
			h: [{ h: [
				"screen",
				"lh",
				...N()
			] }],
			"min-h": [{ "min-h": [
				"screen",
				"lh",
				"none",
				...N()
			] }],
			"max-h": [{ "max-h": [
				"screen",
				"lh",
				...N()
			] }],
			"font-size": [{ text: [
				"base",
				n,
				Pe,
				De
			] }],
			"font-smoothing": ["antialiased", "subpixel-antialiased"],
			"font-style": ["italic", "not-italic"],
			"font-weight": [{ font: [
				r,
				Be,
				ke
			] }],
			"font-stretch": [{ "font-stretch": [
				"ultra-condensed",
				"extra-condensed",
				"condensed",
				"semi-condensed",
				"normal",
				"semi-expanded",
				"expanded",
				"extra-expanded",
				"ultra-expanded",
				ve,
				J
			] }],
			"font-family": [{ font: [
				Fe,
				Ae,
				t
			] }],
			"font-features": [{ "font-features": [J] }],
			"fvn-normal": ["normal-nums"],
			"fvn-ordinal": ["ordinal"],
			"fvn-slashed-zero": ["slashed-zero"],
			"fvn-figure": ["lining-nums", "oldstyle-nums"],
			"fvn-spacing": ["proportional-nums", "tabular-nums"],
			"fvn-fraction": ["diagonal-fractions", "stacked-fractions"],
			tracking: [{ tracking: [
				i,
				Y,
				J
			] }],
			"line-clamp": [{ "line-clamp": [
				G,
				"none",
				Y,
				Oe
			] }],
			leading: [{ leading: [a, ...w()] }],
			"list-image": [{ "list-image": [
				"none",
				Y,
				J
			] }],
			"list-style-position": [{ list: ["inside", "outside"] }],
			"list-style-type": [{ list: [
				"disc",
				"decimal",
				"none",
				Y,
				J
			] }],
			"text-alignment": [{ text: [
				"left",
				"center",
				"right",
				"justify",
				"start",
				"end"
			] }],
			"placeholder-color": [{ placeholder: I() }],
			"text-color": [{ text: I() }],
			"text-decoration": [
				"underline",
				"overline",
				"line-through",
				"no-underline"
			],
			"text-decoration-style": [{ decoration: [...ee(), "wavy"] }],
			"text-decoration-thickness": [{ decoration: [
				G,
				"from-font",
				"auto",
				Y,
				De
			] }],
			"text-decoration-color": [{ decoration: I() }],
			"underline-offset": [{ "underline-offset": [
				G,
				"auto",
				Y,
				J
			] }],
			"text-transform": [
				"uppercase",
				"lowercase",
				"capitalize",
				"normal-case"
			],
			"text-overflow": [
				"truncate",
				"text-ellipsis",
				"text-clip"
			],
			"text-wrap": [{ text: [
				"wrap",
				"nowrap",
				"balance",
				"pretty"
			] }],
			indent: [{ indent: w() }],
			"tab-size": [{ tab: [
				K,
				Y,
				J
			] }],
			"vertical-align": [{ align: [
				"baseline",
				"top",
				"middle",
				"bottom",
				"text-top",
				"text-bottom",
				"sub",
				"super",
				Y,
				J
			] }],
			whitespace: [{ whitespace: [
				"normal",
				"nowrap",
				"pre",
				"pre-line",
				"pre-wrap",
				"break-spaces"
			] }],
			break: [{ break: [
				"normal",
				"words",
				"all",
				"keep"
			] }],
			wrap: [{ wrap: [
				"break-word",
				"anywhere",
				"normal"
			] }],
			hyphens: [{ hyphens: [
				"none",
				"manual",
				"auto"
			] }],
			content: [{ content: [
				"none",
				Y,
				J
			] }],
			"bg-attachment": [{ bg: [
				"fixed",
				"local",
				"scroll"
			] }],
			"bg-clip": [{ "bg-clip": [
				"border",
				"padding",
				"content",
				"text"
			] }],
			"bg-origin": [{ "bg-origin": [
				"border",
				"padding",
				"content"
			] }],
			"bg-position": [{ bg: L() }],
			"bg-repeat": [{ bg: R() }],
			"bg-size": [{ bg: z() }],
			"bg-image": [{ bg: [
				"none",
				{
					linear: [
						{ to: [
							"t",
							"tr",
							"r",
							"br",
							"b",
							"bl",
							"l",
							"tl"
						] },
						K,
						Y,
						J
					],
					radial: [
						"",
						Y,
						J
					],
					conic: [
						K,
						Y,
						J
					]
				},
				Re,
				Me
			] }],
			"bg-color": [{ bg: I() }],
			"gradient-from-pos": [{ from: B() }],
			"gradient-via-pos": [{ via: B() }],
			"gradient-to-pos": [{ to: B() }],
			"gradient-from": [{ from: I() }],
			"gradient-via": [{ via: I() }],
			"gradient-to": [{ to: I() }],
			rounded: [{ rounded: V() }],
			"rounded-s": [{ "rounded-s": V() }],
			"rounded-e": [{ "rounded-e": V() }],
			"rounded-t": [{ "rounded-t": V() }],
			"rounded-r": [{ "rounded-r": V() }],
			"rounded-b": [{ "rounded-b": V() }],
			"rounded-l": [{ "rounded-l": V() }],
			"rounded-ss": [{ "rounded-ss": V() }],
			"rounded-se": [{ "rounded-se": V() }],
			"rounded-ee": [{ "rounded-ee": V() }],
			"rounded-es": [{ "rounded-es": V() }],
			"rounded-tl": [{ "rounded-tl": V() }],
			"rounded-tr": [{ "rounded-tr": V() }],
			"rounded-br": [{ "rounded-br": V() }],
			"rounded-bl": [{ "rounded-bl": V() }],
			"border-w": [{ border: H() }],
			"border-w-x": [{ "border-x": H() }],
			"border-w-y": [{ "border-y": H() }],
			"border-w-s": [{ "border-s": H() }],
			"border-w-e": [{ "border-e": H() }],
			"border-w-bs": [{ "border-bs": H() }],
			"border-w-be": [{ "border-be": H() }],
			"border-w-t": [{ "border-t": H() }],
			"border-w-r": [{ "border-r": H() }],
			"border-w-b": [{ "border-b": H() }],
			"border-w-l": [{ "border-l": H() }],
			"divide-x": [{ "divide-x": H() }],
			"divide-x-reverse": ["divide-x-reverse"],
			"divide-y": [{ "divide-y": H() }],
			"divide-y-reverse": ["divide-y-reverse"],
			"border-style": [{ border: [
				...ee(),
				"hidden",
				"none"
			] }],
			"divide-style": [{ divide: [
				...ee(),
				"hidden",
				"none"
			] }],
			"border-color": [{ border: I() }],
			"border-color-x": [{ "border-x": I() }],
			"border-color-y": [{ "border-y": I() }],
			"border-color-s": [{ "border-s": I() }],
			"border-color-e": [{ "border-e": I() }],
			"border-color-bs": [{ "border-bs": I() }],
			"border-color-be": [{ "border-be": I() }],
			"border-color-t": [{ "border-t": I() }],
			"border-color-r": [{ "border-r": I() }],
			"border-color-b": [{ "border-b": I() }],
			"border-color-l": [{ "border-l": I() }],
			"divide-color": [{ divide: I() }],
			"outline-style": [{ outline: [
				...ee(),
				"none",
				"hidden"
			] }],
			"outline-offset": [{ "outline-offset": [
				G,
				Y,
				J
			] }],
			"outline-w": [{ outline: [
				"",
				G,
				Pe,
				De
			] }],
			"outline-color": [{ outline: I() }],
			shadow: [{ shadow: [
				"",
				"none",
				u,
				ze,
				Ne
			] }],
			"shadow-color": [{ shadow: I() }],
			"inset-shadow": [{ "inset-shadow": [
				"none",
				d,
				ze,
				Ne
			] }],
			"inset-shadow-color": [{ "inset-shadow": I() }],
			"ring-w": [{ ring: H() }],
			"ring-w-inset": ["ring-inset"],
			"ring-color": [{ ring: I() }],
			"ring-offset-w": [{ "ring-offset": [G, De] }],
			"ring-offset-color": [{ "ring-offset": I() }],
			"inset-ring-w": [{ "inset-ring": H() }],
			"inset-ring-color": [{ "inset-ring": I() }],
			"text-shadow": [{ "text-shadow": [
				"none",
				f,
				ze,
				Ne
			] }],
			"text-shadow-color": [{ "text-shadow": I() }],
			opacity: [{ opacity: [
				G,
				Y,
				J
			] }],
			"mix-blend": [{ "mix-blend": [
				...te(),
				"plus-darker",
				"plus-lighter"
			] }],
			"bg-blend": [{ "bg-blend": te() }],
			"mask-clip": [{ "mask-clip": [
				"border",
				"padding",
				"content",
				"fill",
				"stroke",
				"view"
			] }, "mask-no-clip"],
			"mask-composite": [{ mask: [
				"add",
				"subtract",
				"intersect",
				"exclude"
			] }],
			"mask-image-linear-pos": [{ "mask-linear": [G] }],
			"mask-image-linear-from-pos": [{ "mask-linear-from": U() }],
			"mask-image-linear-to-pos": [{ "mask-linear-to": U() }],
			"mask-image-linear-from-color": [{ "mask-linear-from": I() }],
			"mask-image-linear-to-color": [{ "mask-linear-to": I() }],
			"mask-image-t-from-pos": [{ "mask-t-from": U() }],
			"mask-image-t-to-pos": [{ "mask-t-to": U() }],
			"mask-image-t-from-color": [{ "mask-t-from": I() }],
			"mask-image-t-to-color": [{ "mask-t-to": I() }],
			"mask-image-r-from-pos": [{ "mask-r-from": U() }],
			"mask-image-r-to-pos": [{ "mask-r-to": U() }],
			"mask-image-r-from-color": [{ "mask-r-from": I() }],
			"mask-image-r-to-color": [{ "mask-r-to": I() }],
			"mask-image-b-from-pos": [{ "mask-b-from": U() }],
			"mask-image-b-to-pos": [{ "mask-b-to": U() }],
			"mask-image-b-from-color": [{ "mask-b-from": I() }],
			"mask-image-b-to-color": [{ "mask-b-to": I() }],
			"mask-image-l-from-pos": [{ "mask-l-from": U() }],
			"mask-image-l-to-pos": [{ "mask-l-to": U() }],
			"mask-image-l-from-color": [{ "mask-l-from": I() }],
			"mask-image-l-to-color": [{ "mask-l-to": I() }],
			"mask-image-x-from-pos": [{ "mask-x-from": U() }],
			"mask-image-x-to-pos": [{ "mask-x-to": U() }],
			"mask-image-x-from-color": [{ "mask-x-from": I() }],
			"mask-image-x-to-color": [{ "mask-x-to": I() }],
			"mask-image-y-from-pos": [{ "mask-y-from": U() }],
			"mask-image-y-to-pos": [{ "mask-y-to": U() }],
			"mask-image-y-from-color": [{ "mask-y-from": I() }],
			"mask-image-y-to-color": [{ "mask-y-to": I() }],
			"mask-image-radial": [{ "mask-radial": [Y, J] }],
			"mask-image-radial-from-pos": [{ "mask-radial-from": U() }],
			"mask-image-radial-to-pos": [{ "mask-radial-to": U() }],
			"mask-image-radial-from-color": [{ "mask-radial-from": I() }],
			"mask-image-radial-to-color": [{ "mask-radial-to": I() }],
			"mask-image-radial-shape": [{ "mask-radial": ["circle", "ellipse"] }],
			"mask-image-radial-size": [{ "mask-radial": [{
				closest: ["side", "corner"],
				farthest: ["side", "corner"]
			}] }],
			"mask-image-radial-pos": [{ "mask-radial-at": b() }],
			"mask-image-conic-pos": [{ "mask-conic": [G] }],
			"mask-image-conic-from-pos": [{ "mask-conic-from": U() }],
			"mask-image-conic-to-pos": [{ "mask-conic-to": U() }],
			"mask-image-conic-from-color": [{ "mask-conic-from": I() }],
			"mask-image-conic-to-color": [{ "mask-conic-to": I() }],
			"mask-mode": [{ mask: [
				"alpha",
				"luminance",
				"match"
			] }],
			"mask-origin": [{ "mask-origin": [
				"border",
				"padding",
				"content",
				"fill",
				"stroke",
				"view"
			] }],
			"mask-position": [{ mask: L() }],
			"mask-repeat": [{ mask: R() }],
			"mask-size": [{ mask: z() }],
			"mask-type": [{ "mask-type": ["alpha", "luminance"] }],
			"mask-image": [{ mask: [
				"none",
				Y,
				J
			] }],
			filter: [{ filter: [
				"",
				"none",
				Y,
				J
			] }],
			blur: [{ blur: ne() }],
			brightness: [{ brightness: [
				G,
				Y,
				J
			] }],
			contrast: [{ contrast: [
				G,
				Y,
				J
			] }],
			"drop-shadow": [{ "drop-shadow": [
				"",
				"none",
				p,
				ze,
				Ne
			] }],
			"drop-shadow-color": [{ "drop-shadow": I() }],
			grayscale: [{ grayscale: [
				"",
				G,
				Y,
				J
			] }],
			"hue-rotate": [{ "hue-rotate": [
				G,
				Y,
				J
			] }],
			invert: [{ invert: [
				"",
				G,
				Y,
				J
			] }],
			saturate: [{ saturate: [
				G,
				Y,
				J
			] }],
			sepia: [{ sepia: [
				"",
				G,
				Y,
				J
			] }],
			"backdrop-filter": [{ "backdrop-filter": [
				"",
				"none",
				Y,
				J
			] }],
			"backdrop-blur": [{ "backdrop-blur": ne() }],
			"backdrop-brightness": [{ "backdrop-brightness": [
				G,
				Y,
				J
			] }],
			"backdrop-contrast": [{ "backdrop-contrast": [
				G,
				Y,
				J
			] }],
			"backdrop-grayscale": [{ "backdrop-grayscale": [
				"",
				G,
				Y,
				J
			] }],
			"backdrop-hue-rotate": [{ "backdrop-hue-rotate": [
				G,
				Y,
				J
			] }],
			"backdrop-invert": [{ "backdrop-invert": [
				"",
				G,
				Y,
				J
			] }],
			"backdrop-opacity": [{ "backdrop-opacity": [
				G,
				Y,
				J
			] }],
			"backdrop-saturate": [{ "backdrop-saturate": [
				G,
				Y,
				J
			] }],
			"backdrop-sepia": [{ "backdrop-sepia": [
				"",
				G,
				Y,
				J
			] }],
			"border-collapse": [{ border: ["collapse", "separate"] }],
			"border-spacing": [{ "border-spacing": w() }],
			"border-spacing-x": [{ "border-spacing-x": w() }],
			"border-spacing-y": [{ "border-spacing-y": w() }],
			"table-layout": [{ table: ["auto", "fixed"] }],
			caption: [{ caption: ["top", "bottom"] }],
			transition: [{ transition: [
				"",
				"all",
				"colors",
				"opacity",
				"shadow",
				"transform",
				"none",
				Y,
				J
			] }],
			"transition-behavior": [{ transition: ["normal", "discrete"] }],
			duration: [{ duration: [
				G,
				"initial",
				Y,
				J
			] }],
			ease: [{ ease: [
				"linear",
				"initial",
				_,
				Y,
				J
			] }],
			delay: [{ delay: [
				G,
				Y,
				J
			] }],
			animate: [{ animate: [
				"none",
				v,
				Y,
				J
			] }],
			backface: [{ backface: ["hidden", "visible"] }],
			perspective: [{ perspective: [
				h,
				Y,
				J
			] }],
			"perspective-origin": [{ "perspective-origin": x() }],
			rotate: [{ rotate: re() }],
			"rotate-x": [{ "rotate-x": re() }],
			"rotate-y": [{ "rotate-y": re() }],
			"rotate-z": [{ "rotate-z": re() }],
			scale: [{ scale: ie() }],
			"scale-x": [{ "scale-x": ie() }],
			"scale-y": [{ "scale-y": ie() }],
			"scale-z": [{ "scale-z": ie() }],
			"scale-3d": ["scale-3d"],
			skew: [{ skew: ae() }],
			"skew-x": [{ "skew-x": ae() }],
			"skew-y": [{ "skew-y": ae() }],
			transform: [{ transform: [
				Y,
				J,
				"",
				"none",
				"gpu",
				"cpu"
			] }],
			"transform-origin": [{ origin: x() }],
			"transform-style": [{ transform: ["3d", "flat"] }],
			translate: [{ translate: oe() }],
			"translate-x": [{ "translate-x": oe() }],
			"translate-y": [{ "translate-y": oe() }],
			"translate-z": [{ "translate-z": oe() }],
			"translate-none": ["translate-none"],
			zoom: [{ zoom: [
				K,
				Y,
				J
			] }],
			accent: [{ accent: I() }],
			appearance: [{ appearance: ["none", "auto"] }],
			"caret-color": [{ caret: I() }],
			"color-scheme": [{ scheme: [
				"normal",
				"dark",
				"light",
				"light-dark",
				"only-dark",
				"only-light"
			] }],
			cursor: [{ cursor: [
				"auto",
				"default",
				"pointer",
				"wait",
				"text",
				"move",
				"help",
				"not-allowed",
				"none",
				"context-menu",
				"progress",
				"cell",
				"crosshair",
				"vertical-text",
				"alias",
				"copy",
				"no-drop",
				"grab",
				"grabbing",
				"all-scroll",
				"col-resize",
				"row-resize",
				"n-resize",
				"e-resize",
				"s-resize",
				"w-resize",
				"ne-resize",
				"nw-resize",
				"se-resize",
				"sw-resize",
				"ew-resize",
				"ns-resize",
				"nesw-resize",
				"nwse-resize",
				"zoom-in",
				"zoom-out",
				Y,
				J
			] }],
			"field-sizing": [{ "field-sizing": ["fixed", "content"] }],
			"pointer-events": [{ "pointer-events": ["auto", "none"] }],
			resize: [{ resize: [
				"none",
				"",
				"y",
				"x"
			] }],
			"scroll-behavior": [{ scroll: ["auto", "smooth"] }],
			"scrollbar-thumb-color": [{ "scrollbar-thumb": I() }],
			"scrollbar-track-color": [{ "scrollbar-track": I() }],
			"scrollbar-gutter": [{ "scrollbar-gutter": [
				"auto",
				"stable",
				"both"
			] }],
			"scrollbar-w": [{ scrollbar: [
				"auto",
				"thin",
				"none"
			] }],
			"scroll-m": [{ "scroll-m": w() }],
			"scroll-mx": [{ "scroll-mx": w() }],
			"scroll-my": [{ "scroll-my": w() }],
			"scroll-ms": [{ "scroll-ms": w() }],
			"scroll-me": [{ "scroll-me": w() }],
			"scroll-mbs": [{ "scroll-mbs": w() }],
			"scroll-mbe": [{ "scroll-mbe": w() }],
			"scroll-mt": [{ "scroll-mt": w() }],
			"scroll-mr": [{ "scroll-mr": w() }],
			"scroll-mb": [{ "scroll-mb": w() }],
			"scroll-ml": [{ "scroll-ml": w() }],
			"scroll-p": [{ "scroll-p": w() }],
			"scroll-px": [{ "scroll-px": w() }],
			"scroll-py": [{ "scroll-py": w() }],
			"scroll-ps": [{ "scroll-ps": w() }],
			"scroll-pe": [{ "scroll-pe": w() }],
			"scroll-pbs": [{ "scroll-pbs": w() }],
			"scroll-pbe": [{ "scroll-pbe": w() }],
			"scroll-pt": [{ "scroll-pt": w() }],
			"scroll-pr": [{ "scroll-pr": w() }],
			"scroll-pb": [{ "scroll-pb": w() }],
			"scroll-pl": [{ "scroll-pl": w() }],
			"snap-align": [{ snap: [
				"start",
				"end",
				"center",
				"align-none"
			] }],
			"snap-stop": [{ snap: ["normal", "always"] }],
			"snap-type": [{ snap: [
				"none",
				"x",
				"y",
				"both"
			] }],
			"snap-strictness": [{ snap: ["mandatory", "proximity"] }],
			touch: [{ touch: [
				"auto",
				"none",
				"manipulation"
			] }],
			"touch-x": [{ "touch-pan": [
				"x",
				"left",
				"right"
			] }],
			"touch-y": [{ "touch-pan": [
				"y",
				"up",
				"down"
			] }],
			"touch-pz": ["touch-pinch-zoom"],
			select: [{ select: [
				"none",
				"text",
				"all",
				"auto"
			] }],
			"will-change": [{ "will-change": [
				"auto",
				"scroll",
				"contents",
				"transform",
				Y,
				J
			] }],
			fill: [{ fill: ["none", ...I()] }],
			"stroke-w": [{ stroke: [
				G,
				Pe,
				De,
				Oe
			] }],
			stroke: [{ stroke: ["none", ...I()] }],
			"forced-color-adjust": [{ "forced-color-adjust": ["auto", "none"] }]
		},
		conflictingClassGroups: {
			"container-named": ["container-type"],
			overflow: ["overflow-x", "overflow-y"],
			overscroll: ["overscroll-x", "overscroll-y"],
			inset: [
				"inset-x",
				"inset-y",
				"inset-bs",
				"inset-be",
				"start",
				"end",
				"top",
				"right",
				"bottom",
				"left"
			],
			"inset-x": ["right", "left"],
			"inset-y": ["top", "bottom"],
			flex: [
				"basis",
				"grow",
				"shrink"
			],
			gap: ["gap-x", "gap-y"],
			p: [
				"px",
				"py",
				"ps",
				"pe",
				"pbs",
				"pbe",
				"pt",
				"pr",
				"pb",
				"pl"
			],
			px: ["pr", "pl"],
			py: ["pt", "pb"],
			m: [
				"mx",
				"my",
				"ms",
				"me",
				"mbs",
				"mbe",
				"mt",
				"mr",
				"mb",
				"ml"
			],
			mx: ["mr", "ml"],
			my: ["mt", "mb"],
			size: ["w", "h"],
			"font-size": ["leading"],
			"fvn-normal": [
				"fvn-ordinal",
				"fvn-slashed-zero",
				"fvn-figure",
				"fvn-spacing",
				"fvn-fraction"
			],
			"fvn-ordinal": ["fvn-normal"],
			"fvn-slashed-zero": ["fvn-normal"],
			"fvn-figure": ["fvn-normal"],
			"fvn-spacing": ["fvn-normal"],
			"fvn-fraction": ["fvn-normal"],
			"line-clamp": ["display", "overflow"],
			rounded: [
				"rounded-s",
				"rounded-e",
				"rounded-t",
				"rounded-r",
				"rounded-b",
				"rounded-l",
				"rounded-ss",
				"rounded-se",
				"rounded-ee",
				"rounded-es",
				"rounded-tl",
				"rounded-tr",
				"rounded-br",
				"rounded-bl"
			],
			"rounded-s": ["rounded-ss", "rounded-es"],
			"rounded-e": ["rounded-se", "rounded-ee"],
			"rounded-t": ["rounded-tl", "rounded-tr"],
			"rounded-r": ["rounded-tr", "rounded-br"],
			"rounded-b": ["rounded-br", "rounded-bl"],
			"rounded-l": ["rounded-tl", "rounded-bl"],
			"border-spacing": ["border-spacing-x", "border-spacing-y"],
			"border-w": [
				"border-w-x",
				"border-w-y",
				"border-w-s",
				"border-w-e",
				"border-w-bs",
				"border-w-be",
				"border-w-t",
				"border-w-r",
				"border-w-b",
				"border-w-l"
			],
			"border-w-x": ["border-w-r", "border-w-l"],
			"border-w-y": ["border-w-t", "border-w-b"],
			"border-color": [
				"border-color-x",
				"border-color-y",
				"border-color-s",
				"border-color-e",
				"border-color-bs",
				"border-color-be",
				"border-color-t",
				"border-color-r",
				"border-color-b",
				"border-color-l"
			],
			"border-color-x": ["border-color-r", "border-color-l"],
			"border-color-y": ["border-color-t", "border-color-b"],
			translate: [
				"translate-x",
				"translate-y",
				"translate-none"
			],
			"translate-none": [
				"translate",
				"translate-x",
				"translate-y",
				"translate-z"
			],
			"scroll-m": [
				"scroll-mx",
				"scroll-my",
				"scroll-ms",
				"scroll-me",
				"scroll-mbs",
				"scroll-mbe",
				"scroll-mt",
				"scroll-mr",
				"scroll-mb",
				"scroll-ml"
			],
			"scroll-mx": ["scroll-mr", "scroll-ml"],
			"scroll-my": ["scroll-mt", "scroll-mb"],
			"scroll-p": [
				"scroll-px",
				"scroll-py",
				"scroll-ps",
				"scroll-pe",
				"scroll-pbs",
				"scroll-pbe",
				"scroll-pt",
				"scroll-pr",
				"scroll-pb",
				"scroll-pl"
			],
			"scroll-px": ["scroll-pr", "scroll-pl"],
			"scroll-py": ["scroll-pt", "scroll-pb"],
			touch: [
				"touch-x",
				"touch-y",
				"touch-pz"
			],
			"touch-x": ["touch"],
			"touch-y": ["touch"],
			"touch-pz": ["touch"]
		},
		conflictingClassGroupModifiers: { "font-size": ["leading"] },
		postfixLookupClassGroups: ["container-type"],
		orderSensitiveModifiers: [
			"*",
			"**",
			"after",
			"backdrop",
			"before",
			"details-content",
			"file",
			"first-letter",
			"first-line",
			"marker",
			"placeholder",
			"selection"
		]
	};
});
//#endregion
//#region src/lib/utils.ts
function X(...e) {
	return Ze(y(e));
}
//#endregion
//#region src/components/HMSymbolIcon/hmsymbol-icon.generated.ts
var Qe = {
	airplane_fill: "󰄓",
	alarm_fill_1: "󰗯",
	arrow_clockwise: "󰃇",
	arrow_counterclockwise: "󰃈",
	arrow_counterclockwise_clock: "󰏕",
	arrow_down_and_rectangle_on_rectangle: "󰐝",
	arrow_down_circle: "󰢝",
	arrow_down_right_and_arrow_up_left: "󰃉",
	arrow_left: "󰃊",
	arrow_left_circle: "󰚟",
	arrow_right: "󰈱",
	arrow_right_circle: "󰚠",
	arrow_right_folder_circle: "󰂺",
	arrow_right_folder_fill: "󰂻",
	arrow_right_up_and_square: "󰃋",
	arrow_up_and_rectangle_on_rectangle: "󰐠",
	arrow_up_circle: "󰃌",
	arrow_up_circle_fill: "󰈲",
	arrow_up_left: "󰈳",
	arrow_up_left_and_arrow_down_right: "󰃍",
	arrow_up_to_line: "󰃏",
	arrowshape_3_triangle_path: "󰓵",
	arrowshape_down_to_line_fill: "󰃐",
	arrowshape_turn_up_right_fill: "󰣂",
	arrowshape_up: "󰈽",
	arrowshape_up_fill: "󰈹",
	arrowshape_up_frame_fill: "󰈺",
	arrowshape_up_left_and_arrowshape_down_right: "󰟮",
	arrowshape_up_to_line_fill: "󰀐",
	arrowtriangle_down_fill: "󰈿",
	arrowtriangle_up_fill: "󰉀",
	asterisk_rectangle_badge_handwritten: "󰋮",
	backward_end_fill: "󰂦",
	battery: "󰄚",
	battery_75percent: "󰙙",
	beidou_satellite_circle_fill: "󰔖",
	beidou_satellite_fill: "󰚭",
	bell_fill: "󰇑",
	bell_slash: "󰇓",
	bell_slash_fill: "󰇒",
	bluetooth: "󰉔",
	bluetooth_slash: "󰉓",
	bolt: "󰉢",
	bolt_filled_on_circle: "󰉟",
	bolt_shield_fill: "󰟱",
	book_open_fill: "󰟉",
	book_pages_fill_1: "󰢿",
	bookmark: "󰀊",
	bookmark_filled_on_bookmark: "󰙚",
	briefcase: "󰙟",
	brush: "󰀍",
	brush_fill: "󰀌",
	calculator_1: "󰡟",
	calendar: "󰏚",
	calendar_badge_clock: "󰏘",
	calendar_fill: "󰏙",
	camera: "󰑛",
	camera_fill: "󰐸",
	camera_filters_fill: "󰠬",
	capture_smiles: "󰗈",
	case_fill: "󰙠",
	celiakeyboard_elevate: "󰒒",
	celiakeyboard_mechanical: "󰋲",
	celiakeyboard_menu_icon_size: "󰋳",
	character_arrow_clockwise: "󰇖",
	character_viewfinder: "󰇘",
	checkmark: "󰀓",
	checkmark_circle: "󰀏",
	checkmark_circle_fill: "󰀎",
	checkmark_clipboard_fill: "󰆊",
	checkmark_shield: "󰑞",
	checkmark_shield_fill: "󰑝",
	checkmark_square: "󰀒",
	checkmark_square_fill: "󰇚",
	checkmark_square_on_square: "󰀑",
	checkmark_square_on_square_fill: "󰇙",
	chevron_down: "󰃛",
	chevron_down_2_circle: "󰛀",
	chevron_down_circle: "󰛁",
	chevron_left: "󰃚",
	chevron_left_2: "󰛂",
	chevron_left_circle: "󰛃",
	chevron_right: "󰃙",
	chevron_right_circle: "󰛄",
	chevron_up: "󰃘",
	chevron_up_2: "󰛆",
	chevron_up_2_circle: "󰛅",
	chevron_up_circle: "󰑟",
	children: "󰙣",
	circle: "󰀇",
	circle_dashed: "󰄴",
	circle_lefthalf_inset_filled: "󰁜",
	circle_righthalf_inset_filled: "󰁝",
	circle_viewfinder: "󰄣",
	clean: "󰀖",
	clean_fill: "󰀕",
	clock: "󰏝",
	clock_fill: "󰏜",
	close_sidebar: "󰢟",
	crop_rotate: "󰅡",
	cut: "󰁟",
	delete_left: "󰃝",
	delete_left_fill: "󰕁",
	dial: "󰂁",
	discover_fill: "󰇛",
	doc: "󰂽",
	doc_plaintext: "󰃁",
	doc_plaintext_and_pencil: "󰖯",
	doc_plaintext_and_pencil_fill: "󰙩",
	doc_plaintext_fill: "󰃂",
	doc_text: "󰂼",
	doc_text_badge_arrow_up: "󰖱",
	doc_text_badge_checkmark: "󰃄",
	doc_text_badge_magnifyingglass: "󰖳",
	doc_text_fill: "󰂿",
	dot_grid_1x2: "󰁠",
	dot_grid_2x2: "󰁡",
	dot_radiowaves_left_and_right: "󰉹",
	dot_video_fill: "󰂂",
	drop: "󰁣",
	drop_bottomrighthalf_inset_filled: "󰄶",
	ear: "󰗉",
	ellipsis_bubble: "󰑳",
	ellipsis_message: "󰂅",
	ellipsis_message_fill: "󰂄",
	envelope: "󰂈",
	envelope_fill: "󰂉",
	envelope_open_fill: "󰂊",
	eraser_line: "󰁥",
	exclamationmark: "󰄋",
	exclamationmark_circle: "󰄉",
	exclamationmark_shield_fill: "󰑷",
	exclamationmark_triangle_fill: "󰛗",
	externaldrive: "󰃟",
	externaldrive_fill: "󰃞",
	externaldrive_fill_3: "󰄞",
	eye: "󰄠",
	eye_slash: "󰄟",
	face: "󰗊",
	face_smiling: "󰗐",
	fast_forward: "󰙫",
	figure_arms_open: "󰗑",
	figure_running: "󰟕",
	flag: "󰆬",
	flashlight_off_fill: "󰀚",
	flashlight_on_fill: "󰀜",
	flower: "󰊄",
	folder: "󰃅",
	folder_badge_eye: "󰖽",
	folder_badge_plus: "󰀄",
	folder_fill: "󰃆",
	form: "󰆔",
	forward_end_fill: "󰂧",
	full_screen_fill: "󰕊",
	gearshape: "󰀠",
	gobackward_15: "󰏲",
	gobackward_30: "󰏳",
	goforward_10: "󰏴",
	goforward_15: "󰏵",
	goforward_30: "󰏶",
	grid: "󰙰",
	hand_draw: "󰁦",
	hand_point_up_tap_fill: "󰒄",
	hand_point_up_tap_fill_1: "󰔢",
	hand_point_up_tap_fill_slash: "󰙱",
	hand_raised_hexagon: "󰝃",
	hand_raised_hexagon_fill: "󰒇",
	hand_tap: "󰒊",
	hand_thumbsup_fill: "󰗗",
	hd_square_fill: "󰊊",
	headphones_fill: "󰙲",
	heart: "󰀥",
	heart_fill: "󰀡",
	heart_slash: "󰀤",
	heart_square_stack_fill: "󰔔",
	hotspot: "󰊏",
	house: "󰀧",
	house_fill: "󰀦",
	icloud: "󰊔",
	icloud_slash: "󰊓",
	icloud_slash_fill: "󰊒",
	identify_song: "󰌻",
	indent_right: "󰅣",
	indentation_left: "󰅤",
	info_circle: "󰊖",
	info_shield: "󰊗",
	input_mode: "󰒔",
	key_horizontal: "󰒛",
	key_shield: "󰒞",
	key_shield_fill: "󰒝",
	keyboard_badge_bihua: "󰌂",
	keyboard_badge_cangjie: "󰌃",
	keyboard_badge_handwritten: "󰌆",
	keyboard_badge_spell: "󰌇",
	keyboard_badge_wubi: "󰌈",
	keyboard_badge_zhuyin: "󰌉",
	keyboard_circle: "󰅲",
	keyboard_onehanded_left: "󰌌",
	keyboard_onehanded_right: "󰌍",
	keyboard_square: "󰌎",
	keyboard_thumbmode: "󰌏",
	label: "󰈈",
	lightbulb: "󰊜",
	lightbulb_slash: "󰊚",
	line_arrowtriangle_2_inward: "󰁨",
	line_below_arrowtriangle_up_circle_fill: "󰐖",
	line_below_arrowtriangle_up_fill: "󰐗",
	line_viewfinder: "󰀨",
	link_slash: "󰊠",
	list_bullet: "󰁩",
	list_bullet_circle: "󰅦",
	list_bullet_square_fill: "󰅧",
	list_checkmask: "󰅂",
	list_interrupt: "󰌼",
	list_letter: "󰅄",
	list_number: "󰅃",
	list_square: "󰅅",
	list_square_bill: "󰖿",
	livephoto: "󰗷",
	local_fill: "󰆸",
	location_north_up_right_circle_fill: "󰠍",
	lock: "󰀈",
	lock_fill: "󰓁",
	lock_filled_arrow_counterclockwise: "󰕼",
	lock_open: "󰓄",
	lock_open_fill: "󰓃",
	magnifyingglass: "󰀩",
	map: "󰇂",
	map_badge_local: "󰇀",
	map_slash: "󰇃",
	media_center: "󰙼",
	message: "󰂏",
	message_badge_gearshape_1: "󰝖",
	message_on_message: "󰂎",
	message_on_message_fill: "󰂍",
	mic: "󰀆",
	mic_circle: "󰌔",
	mic_fill: "󰌕",
	mic_slash: "󰝘",
	mic_slash_fill: "󰌗",
	minus: "󰀬",
	minus_circle: "󰀫",
	minus_magnifyingglass: "󰚀",
	mobiledata: "󰊩",
	moon_circle_fill: "󰕮",
	moon_fill: "󰀭",
	moon_slash_circle: "󰕯",
	more: "󰕰",
	movie_fill: "󰓒",
	music: "󰂭",
	music_fill: "󰂪",
	music_note_list: "󰂬",
	navigation: "󰠐",
	nearlink: "󰝜",
	nfc: "󰓗",
	nfc_fill: "󰓖",
	nosign: "󰄎",
	onehand: "󰌘",
	open_sidebar: "󰢧",
	order_play: "󰂮",
	oval: "󰍋",
	paintbrush: "󰟞",
	paintbrush_fill: "󰟝",
	paintpalette: "󰄥",
	paintpalette_fill: "󰄤",
	paperclip: "󰄏",
	paperplane: "󰀰",
	paperplane_right_fill: "󰢨",
	pause: "󰂱",
	pause_round_triangle_fill: "󰡫",
	pencil_line_1: "󰘦",
	pencil_waveform: "󰁬",
	pencil_waveform_fill: "󰘧",
	person: "󰗥",
	person_2: "󰗜",
	person_2_fill: "󰗛",
	person_badge_plus: "󰗟",
	person_crop_circle_fill_1: "󰗳",
	person_filled_badge_plus: "󰗤",
	person_filled_viewfinder: "󰕹",
	person_shield: "󰓞",
	person_shield_fill: "󰓝",
	person_square_fill: "󰕺",
	phone_down_fill: "󰂟",
	phone_fill: "󰂞",
	picture: "󰀃",
	picture_2: "󰓥",
	picture_damage: "󰓩",
	picture_fill: "󰓪",
	pin: "󰀲",
	pin_fill_1: "󰢫",
	play_circle_fill: "󰂲",
	play_fill: "󰂴",
	play_hexagon_fill: "󰠓",
	play_round_rectangle_fill: "󰠔",
	play_video: "󰓮",
	play_video_fill: "󰢬",
	plus: "󰀵",
	plus_magnifyingglass: "󰄧",
	plus_square: "󰣃",
	plus_square_on_square_fill: "󰁭",
	portrait: "󰗇",
	position: "󰇊",
	power: "󰀶",
	puzzle: "󰒠",
	puzzle_fill: "󰒵",
	qrcode: "󰄨",
	questionmark_circle: "󰄀",
	rays: "󰀷",
	record_circle: "󰂷",
	recordingtape: "󰅶",
	recordingtape_rectangle: "󰅵",
	recordingtape_rectangle_fill: "󰅴",
	rectangle: "󰁰",
	rectangle_and_arrowshape_turn_up_right: "󰃕",
	rectangle_and_cut: "󰁯",
	rectangle_on_rectangle: "󰒢",
	rectangle_on_rectangle_fill: "󰒡",
	rectangle_portrait_rotate: "󰀸",
	rectangle_rotate: "󰢭",
	rectangle_split_3x1: "󰔨",
	redo: "󰇴",
	remove_songlist: "󰍣",
	rename: "󰁱",
	repeat: "󰂸",
	repeat_1: "󰂹",
	resolution_video: "󰒣",
	reverse_order: "󰏽",
	rotate_left: "󰍤",
	route_plan: "󰟤",
	satellite: "󰅷",
	satellite_map: "󰝵",
	satellite_map_fill: "󰝴",
	save: "󰀻",
	scope: "󰒦",
	scope_slash: "󰒥",
	selector: "󰌛",
	service: "󰍥",
	share: "󰀽",
	shuffle: "󰂵",
	shutter_photo: "󰒯",
	skip_silence: "󰎻",
	slider_horizontal_2: "󰁲",
	slider_vertical_3: "󰄪",
	smallcircle_filled_circle: "󰅩",
	sort: "󰖁",
	space_1: "󰌜",
	speaker: "󰁄",
	speaker_slash: "󰁃",
	speaker_wave_3: "󰁊",
	speaker_wave_3_slash: "󰖏",
	square: "󰁵",
	square_and_pencil: "󰁳",
	square_and_pencil_fill: "󰁴",
	square_fill_grid_2x2: "󰁋",
	square_grid_2x2: "󰃣",
	square_slash: "󰒴",
	star: "󰁎",
	star_fill: "󰀉",
	staroflife_rectangle: "󰓸",
	stopwatch_2: "󰗰",
	sun_max: "󰁐",
	sun_max_fill: "󰁏",
	sun_min: "󰁑",
	swap: "󰋑",
	swipeup_input: "󰌞",
	template: "󰓿",
	template_fill: "󰓾",
	text_aligncenter: "󰁶",
	text_alignleft: "󰁷",
	text_alignright: "󰁸",
	text_and_arrow_down: "󰁹",
	text_and_arrow_up: "󰁺",
	text_clipboard: "󰆝",
	textformat_size_square: "󰁼",
	timer: "󰐆",
	timer_circle_fill: "󰗶",
	touchid: "󰔇",
	traditional_square: "󰌢",
	transfer_station: "󰞈",
	translate: "󰁾",
	translate_c2e: "󰌣",
	translate_e2c: "󰌤",
	transparency_lock: "󰘹",
	trapezoid_and_line_horizontal: "󰅪",
	trapezoid_and_line_vertical: "󰅫",
	trash: "󰀁",
	trash_fill: "󰁒",
	triangleshape_fill: "󰍫",
	undo: "󰇳",
	vertical_flip: "󰘻",
	video_fill: "󰂣",
	video_slasj_fill: "󰡁",
	vpn_key: "󰞏",
	wifi: "󰀀",
	wifi_slash: "󰚑",
	worldclock: "󰐊",
	worldclock_fill: "󰐉",
	worldclock_fill_2: "󰗱",
	xmark: "󰁖",
	xmark_circle: "󰁕",
	xmark_circle_fill: "󰁔",
	xmark_picture: "󰡂",
	xmark_picture_fill: "󰠡"
}, $e = {
	airplane_fill: "F0113",
	alarm_fill_1: "F05EF",
	arrow_clockwise: "F00C7",
	arrow_counterclockwise: "F00C8",
	arrow_counterclockwise_clock: "F03D5",
	arrow_down_and_rectangle_on_rectangle: "F041D",
	arrow_down_circle: "F089D",
	arrow_down_right_and_arrow_up_left: "F00C9",
	arrow_left: "F00CA",
	arrow_left_circle: "F069F",
	arrow_right: "F0231",
	arrow_right_circle: "F06A0",
	arrow_right_folder_circle: "F00BA",
	arrow_right_folder_fill: "F00BB",
	arrow_right_up_and_square: "F00CB",
	arrow_up_and_rectangle_on_rectangle: "F0420",
	arrow_up_circle: "F00CC",
	arrow_up_circle_fill: "F0232",
	arrow_up_left: "F0233",
	arrow_up_left_and_arrow_down_right: "F00CD",
	arrow_up_to_line: "F00CF",
	arrowshape_3_triangle_path: "F04F5",
	arrowshape_down_to_line_fill: "F00D0",
	arrowshape_turn_up_right_fill: "F08C2",
	arrowshape_up: "F023D",
	arrowshape_up_fill: "F0239",
	arrowshape_up_frame_fill: "F023A",
	arrowshape_up_left_and_arrowshape_down_right: "F07EE",
	arrowshape_up_to_line_fill: "F0010",
	arrowtriangle_down_fill: "F023F",
	arrowtriangle_up_fill: "F0240",
	asterisk_rectangle_badge_handwritten: "F02EE",
	backward_end_fill: "F00A6",
	battery: "F011A",
	battery_75percent: "F0659",
	beidou_satellite_circle_fill: "F0516",
	beidou_satellite_fill: "F06AD",
	bell_fill: "F01D1",
	bell_slash: "F01D3",
	bell_slash_fill: "F01D2",
	bluetooth: "F0254",
	bluetooth_slash: "F0253",
	bolt: "F0262",
	bolt_filled_on_circle: "F025F",
	bolt_shield_fill: "F07F1",
	book_open_fill: "F07C9",
	book_pages_fill_1: "F08BF",
	bookmark: "F000A",
	bookmark_filled_on_bookmark: "F065A",
	briefcase: "F065F",
	brush: "F000D",
	brush_fill: "F000C",
	calculator_1: "F085F",
	calendar: "F03DA",
	calendar_badge_clock: "F03D8",
	calendar_fill: "F03D9",
	camera: "F045B",
	camera_fill: "F0438",
	camera_filters_fill: "F082C",
	capture_smiles: "F05C8",
	case_fill: "F0660",
	celiakeyboard_elevate: "F0492",
	celiakeyboard_mechanical: "F02F2",
	celiakeyboard_menu_icon_size: "F02F3",
	character_arrow_clockwise: "F01D6",
	character_viewfinder: "F01D8",
	checkmark: "F0013",
	checkmark_circle: "F000F",
	checkmark_circle_fill: "F000E",
	checkmark_clipboard_fill: "F018A",
	checkmark_shield: "F045E",
	checkmark_shield_fill: "F045D",
	checkmark_square: "F0012",
	checkmark_square_fill: "F01DA",
	checkmark_square_on_square: "F0011",
	checkmark_square_on_square_fill: "F01D9",
	chevron_down: "F00DB",
	chevron_down_2_circle: "F06C0",
	chevron_down_circle: "F06C1",
	chevron_left: "F00DA",
	chevron_left_2: "F06C2",
	chevron_left_circle: "F06C3",
	chevron_right: "F00D9",
	chevron_right_circle: "F06C4",
	chevron_up: "F00D8",
	chevron_up_2: "F06C6",
	chevron_up_2_circle: "F06C5",
	chevron_up_circle: "F045F",
	children: "F0663",
	circle: "F0007",
	circle_dashed: "F0134",
	circle_lefthalf_inset_filled: "F005C",
	circle_righthalf_inset_filled: "F005D",
	circle_viewfinder: "F0123",
	clean: "F0016",
	clean_fill: "F0015",
	clock: "F03DD",
	clock_fill: "F03DC",
	close_sidebar: "F089F",
	crop_rotate: "F0161",
	cut: "F005F",
	delete_left: "F00DD",
	delete_left_fill: "F0541",
	dial: "F0081",
	discover_fill: "F01DB",
	doc: "F00BD",
	doc_plaintext: "F00C1",
	doc_plaintext_and_pencil: "F05AF",
	doc_plaintext_and_pencil_fill: "F0669",
	doc_plaintext_fill: "F00C2",
	doc_text: "F00BC",
	doc_text_badge_arrow_up: "F05B1",
	doc_text_badge_checkmark: "F00C4",
	doc_text_badge_magnifyingglass: "F05B3",
	doc_text_fill: "F00BF",
	dot_grid_1x2: "F0060",
	dot_grid_2x2: "F0061",
	dot_radiowaves_left_and_right: "F0279",
	dot_video_fill: "F0082",
	drop: "F0063",
	drop_bottomrighthalf_inset_filled: "F0136",
	ear: "F05C9",
	ellipsis_bubble: "F0473",
	ellipsis_message: "F0085",
	ellipsis_message_fill: "F0084",
	envelope: "F0088",
	envelope_fill: "F0089",
	envelope_open_fill: "F008A",
	eraser_line: "F0065",
	exclamationmark: "F010B",
	exclamationmark_circle: "F0109",
	exclamationmark_shield_fill: "F0477",
	exclamationmark_triangle_fill: "F06D7",
	externaldrive: "F00DF",
	externaldrive_fill: "F00DE",
	externaldrive_fill_3: "F011E",
	eye: "F0120",
	eye_slash: "F011F",
	face: "F05CA",
	face_smiling: "F05D0",
	fast_forward: "F066B",
	figure_arms_open: "F05D1",
	figure_running: "F07D5",
	flag: "F01AC",
	flashlight_off_fill: "F001A",
	flashlight_on_fill: "F001C",
	flower: "F0284",
	folder: "F00C5",
	folder_badge_eye: "F05BD",
	folder_badge_plus: "F0004",
	folder_fill: "F00C6",
	form: "F0194",
	forward_end_fill: "F00A7",
	full_screen_fill: "F054A",
	gearshape: "F0020",
	gobackward_15: "F03F2",
	gobackward_30: "F03F3",
	goforward_10: "F03F4",
	goforward_15: "F03F5",
	goforward_30: "F03F6",
	grid: "F0670",
	hand_draw: "F0066",
	hand_point_up_tap_fill: "F0484",
	hand_point_up_tap_fill_1: "F0522",
	hand_point_up_tap_fill_slash: "F0671",
	hand_raised_hexagon: "F0743",
	hand_raised_hexagon_fill: "F0487",
	hand_tap: "F048A",
	hand_thumbsup_fill: "F05D7",
	hd_square_fill: "F028A",
	headphones_fill: "F0672",
	heart: "F0025",
	heart_fill: "F0021",
	heart_slash: "F0024",
	heart_square_stack_fill: "F0514",
	hotspot: "F028F",
	house: "F0027",
	house_fill: "F0026",
	icloud: "F0294",
	icloud_slash: "F0293",
	icloud_slash_fill: "F0292",
	identify_song: "F033B",
	indent_right: "F0163",
	indentation_left: "F0164",
	info_circle: "F0296",
	info_shield: "F0297",
	input_mode: "F0494",
	key_horizontal: "F049B",
	key_shield: "F049E",
	key_shield_fill: "F049D",
	keyboard_badge_bihua: "F0302",
	keyboard_badge_cangjie: "F0303",
	keyboard_badge_handwritten: "F0306",
	keyboard_badge_spell: "F0307",
	keyboard_badge_wubi: "F0308",
	keyboard_badge_zhuyin: "F0309",
	keyboard_circle: "F0172",
	keyboard_onehanded_left: "F030C",
	keyboard_onehanded_right: "F030D",
	keyboard_square: "F030E",
	keyboard_thumbmode: "F030F",
	label: "F0208",
	lightbulb: "F029C",
	lightbulb_slash: "F029A",
	line_arrowtriangle_2_inward: "F0068",
	line_below_arrowtriangle_up_circle_fill: "F0416",
	line_below_arrowtriangle_up_fill: "F0417",
	line_viewfinder: "F0028",
	link_slash: "F02A0",
	list_bullet: "F0069",
	list_bullet_circle: "F0166",
	list_bullet_square_fill: "F0167",
	list_checkmask: "F0142",
	list_interrupt: "F033C",
	list_letter: "F0144",
	list_number: "F0143",
	list_square: "F0145",
	list_square_bill: "F05BF",
	livephoto: "F05F7",
	local_fill: "F01B8",
	location_north_up_right_circle_fill: "F080D",
	lock: "F0008",
	lock_fill: "F04C1",
	lock_filled_arrow_counterclockwise: "F057C",
	lock_open: "F04C4",
	lock_open_fill: "F04C3",
	magnifyingglass: "F0029",
	map: "F01C2",
	map_badge_local: "F01C0",
	map_slash: "F01C3",
	media_center: "F067C",
	message: "F008F",
	message_badge_gearshape_1: "F0756",
	message_on_message: "F008E",
	message_on_message_fill: "F008D",
	mic: "F0006",
	mic_circle: "F0314",
	mic_fill: "F0315",
	mic_slash: "F0758",
	mic_slash_fill: "F0317",
	minus: "F002C",
	minus_circle: "F002B",
	minus_magnifyingglass: "F0680",
	mobiledata: "F02A9",
	moon_circle_fill: "F056E",
	moon_fill: "F002D",
	moon_slash_circle: "F056F",
	more: "F0570",
	movie_fill: "F04D2",
	music: "F00AD",
	music_fill: "F00AA",
	music_note_list: "F00AC",
	navigation: "F0810",
	nearlink: "F075C",
	nfc: "F04D7",
	nfc_fill: "F04D6",
	nosign: "F010E",
	onehand: "F0318",
	open_sidebar: "F08A7",
	order_play: "F00AE",
	oval: "F034B",
	paintbrush: "F07DE",
	paintbrush_fill: "F07DD",
	paintpalette: "F0125",
	paintpalette_fill: "F0124",
	paperclip: "F010F",
	paperplane: "F0030",
	paperplane_right_fill: "F08A8",
	pause: "F00B1",
	pause_round_triangle_fill: "F086B",
	pencil_line_1: "F0626",
	pencil_waveform: "F006C",
	pencil_waveform_fill: "F0627",
	person: "F05E5",
	person_2: "F05DC",
	person_2_fill: "F05DB",
	person_badge_plus: "F05DF",
	person_crop_circle_fill_1: "F05F3",
	person_filled_badge_plus: "F05E4",
	person_filled_viewfinder: "F0579",
	person_shield: "F04DE",
	person_shield_fill: "F04DD",
	person_square_fill: "F057A",
	phone_down_fill: "F009F",
	phone_fill: "F009E",
	picture: "F0003",
	picture_2: "F04E5",
	picture_damage: "F04E9",
	picture_fill: "F04EA",
	pin: "F0032",
	pin_fill_1: "F08AB",
	play_circle_fill: "F00B2",
	play_fill: "F00B4",
	play_hexagon_fill: "F0813",
	play_round_rectangle_fill: "F0814",
	play_video: "F04EE",
	play_video_fill: "F08AC",
	plus: "F0035",
	plus_magnifyingglass: "F0127",
	plus_square: "F08C3",
	plus_square_on_square_fill: "F006D",
	portrait: "F05C7",
	position: "F01CA",
	power: "F0036",
	puzzle: "F04A0",
	puzzle_fill: "F04B5",
	qrcode: "F0128",
	questionmark_circle: "F0100",
	rays: "F0037",
	record_circle: "F00B7",
	recordingtape: "F0176",
	recordingtape_rectangle: "F0175",
	recordingtape_rectangle_fill: "F0174",
	rectangle: "F0070",
	rectangle_and_arrowshape_turn_up_right: "F00D5",
	rectangle_and_cut: "F006F",
	rectangle_on_rectangle: "F04A2",
	rectangle_on_rectangle_fill: "F04A1",
	rectangle_portrait_rotate: "F0038",
	rectangle_rotate: "F08AD",
	rectangle_split_3x1: "F0528",
	redo: "F01F4",
	remove_songlist: "F0363",
	rename: "F0071",
	repeat: "F00B8",
	repeat_1: "F00B9",
	resolution_video: "F04A3",
	reverse_order: "F03FD",
	rotate_left: "F0364",
	route_plan: "F07E4",
	satellite: "F0177",
	satellite_map: "F0775",
	satellite_map_fill: "F0774",
	save: "F003B",
	scope: "F04A6",
	scope_slash: "F04A5",
	selector: "F031B",
	service: "F0365",
	share: "F003D",
	shuffle: "F00B5",
	shutter_photo: "F04AF",
	skip_silence: "F03BB",
	slider_horizontal_2: "F0072",
	slider_vertical_3: "F012A",
	smallcircle_filled_circle: "F0169",
	sort: "F0581",
	space_1: "F031C",
	speaker: "F0044",
	speaker_slash: "F0043",
	speaker_wave_3: "F004A",
	speaker_wave_3_slash: "F058F",
	square: "F0075",
	square_and_pencil: "F0073",
	square_and_pencil_fill: "F0074",
	square_fill_grid_2x2: "F004B",
	square_grid_2x2: "F00E3",
	square_slash: "F04B4",
	star: "F004E",
	star_fill: "F0009",
	staroflife_rectangle: "F04F8",
	stopwatch_2: "F05F0",
	sun_max: "F0050",
	sun_max_fill: "F004F",
	sun_min: "F0051",
	swap: "F02D1",
	swipeup_input: "F031E",
	template: "F04FF",
	template_fill: "F04FE",
	text_aligncenter: "F0076",
	text_alignleft: "F0077",
	text_alignright: "F0078",
	text_and_arrow_down: "F0079",
	text_and_arrow_up: "F007A",
	text_clipboard: "F019D",
	textformat_size_square: "F007C",
	timer: "F0406",
	timer_circle_fill: "F05F6",
	touchid: "F0507",
	traditional_square: "F0322",
	transfer_station: "F0788",
	translate: "F007E",
	translate_c2e: "F0323",
	translate_e2c: "F0324",
	transparency_lock: "F0639",
	trapezoid_and_line_horizontal: "F016A",
	trapezoid_and_line_vertical: "F016B",
	trash: "F0001",
	trash_fill: "F0052",
	triangleshape_fill: "F036B",
	undo: "F01F3",
	vertical_flip: "F063B",
	video_fill: "F00A3",
	video_slasj_fill: "F0841",
	vpn_key: "F078F",
	wifi: "F0000",
	wifi_slash: "F0691",
	worldclock: "F040A",
	worldclock_fill: "F0409",
	worldclock_fill_2: "F05F1",
	xmark: "F0056",
	xmark_circle: "F0055",
	xmark_circle_fill: "F0054",
	xmark_picture: "F0842",
	xmark_picture_fill: "F0821"
}, et = {
	square_dashed: "󰄴",
	tv: "󰀡",
	stopwatch: "󰗰",
	mic: "󰀆",
	mic_fill: "󰌕",
	questionmark_circle: "󰄀",
	triangle_down_fill: "󰈿",
	segmented_button_highlight: "󰄯",
	plus_list: "󰅖"
}, tt = {
	square_dashed: "F0134",
	tv: "F0021",
	stopwatch: "F05F0",
	mic: "F0006",
	mic_fill: "F0315",
	questionmark_circle: "F0100",
	triangle_down_fill: "F023F",
	segmented_button_highlight: "F012F",
	plus_list: "F0156"
}, nt = {
	...Qe,
	...et
}, rt = {
	...$e,
	...tt
};
//#endregion
//#region src/components/HMSymbolIcon/hmsymbol-icon.tsx
function Z({ className: e, decorative: t = !0, name: n, size: r = 24, style: i, title: a, ...o }) {
	let s = it(n);
	return /* @__PURE__ */ m("span", {
		"aria-hidden": t ? "true" : void 0,
		"aria-label": t ? void 0 : a,
		className: X("hm-symbol-icon", e),
		role: t ? void 0 : "img",
		style: {
			fontSize: typeof r == "number" ? `${r}px` : r,
			width: typeof r == "number" ? `${r}px` : r,
			height: typeof r == "number" ? `${r}px` : r,
			...i
		},
		title: a,
		...o,
		children: s
	});
}
function it(e) {
	if (e in nt) return nt[e];
	let t = /^\\u\{([0-9a-fA-F]+)\}$/.exec(e);
	return t ? String.fromCodePoint(Number.parseInt(t[1], 16)) : e;
}
//#endregion
//#region src/components/HMSymbolIcon/index.ts
var at = /* @__PURE__ */ _({
	HMSymbolIcon: () => Z,
	hmSymbolGlyphs: () => nt,
	hmSymbolGlyphsGenerated: () => Qe,
	hmSymbolUnicodeByName: () => $e,
	hmSymbolUnicodes: () => rt
}), ot = [
	"Max",
	"Larger",
	"Medium",
	"Small",
	"Mini"
], st = {
	Max: "hm-card--max",
	Larger: "hm-card--larger",
	Medium: "hm-card--medium",
	Small: "hm-card--small",
	Mini: "hm-card--mini"
};
function ct() {
	return /* @__PURE__ */ h("span", {
		className: "hm-card__icon-button",
		"aria-hidden": "true",
		children: [/* @__PURE__ */ m("span", { className: "hm-card__icon-button-bg" }), /* @__PURE__ */ m(Z, {
			className: "hm-card__icon-glyph",
			name: "square_dashed",
			size: 24
		})]
	});
}
function lt({ 尺寸: e = "Medium", children: t, hideIconButton: n = !1, className: r, ...i }) {
	return /* @__PURE__ */ h("div", {
		className: X("hm-card", st[e], r),
		"data-size": e,
		...i,
		children: [t, !n && e === "Mini" ? /* @__PURE__ */ h(p, { children: [/* @__PURE__ */ h("span", {
			className: "hm-card__icon-button hm-card__icon-button--left",
			"aria-hidden": "true",
			children: [/* @__PURE__ */ m("span", { className: "hm-card__icon-button-bg" }), /* @__PURE__ */ m(Z, {
				className: "hm-card__icon-glyph",
				name: "square_dashed",
				size: 24
			})]
		}), /* @__PURE__ */ h("span", {
			className: "hm-card__icon-button hm-card__icon-button--right",
			"aria-hidden": "true",
			children: [/* @__PURE__ */ m("span", { className: "hm-card__icon-button-bg" }), /* @__PURE__ */ m(Z, {
				className: "hm-card__icon-glyph",
				name: "square_dashed",
				size: 24
			})]
		})] }) : !n && /* @__PURE__ */ m(ct, {})]
	});
}
//#endregion
//#region src/components/Container/Card/index.ts
var ut = /* @__PURE__ */ _({
	Card: () => lt,
	card尺寸Options: () => ot
}), dt = [
	"content",
	"content+button",
	"title+content_single line",
	"title+content_2lines",
	"title+content+2 button",
	"title+content+3 button",
	"progress bar",
	"progress bar+button"
], ft = (e) => e.startsWith("title+content"), pt = (e) => e !== "progress bar" && e !== "progress bar+button", mt = (e) => e.includes("button"), ht = (e) => e.includes("progress bar");
function gt(e) {
	switch (e) {
		case "content+button":
		case "progress bar+button": return [{
			id: "primary",
			label: "BUTTON",
			variant: "normal"
		}];
		case "title+content+2 button": return [{
			id: "cancel",
			label: "BUTTON",
			variant: "normal"
		}, {
			id: "confirm",
			label: "BUTTON",
			variant: "emphasize"
		}];
		case "title+content+3 button": return [
			{
				id: "action-1",
				label: "BUTTON",
				variant: "normal"
			},
			{
				id: "action-2",
				label: "BUTTON",
				variant: "normal"
			},
			{
				id: "action-3",
				label: "BUTTON",
				variant: "emphasize"
			}
		];
		default: return [];
	}
}
function _t(e) {
	switch (e) {
		case "title+content+3 button": return "vertical";
		case "title+content+2 button": return "horizontal-emphasize";
		default: return "horizontal";
	}
}
function vt() {
	return /* @__PURE__ */ m(Z, {
		name: "xmark_circle_fill",
		size: 24
	});
}
function yt(e) {
	return e.replace(/\+/g, "-plus-").replace(/ /g, "-");
}
function bt({ 类型: e = "content", title: t = "Title", content: n = "AAAAAAAAAAAAAAAAAAAAAAAA", progress: r = 50, buttons: i, onClose: a, className: o, ...s }) {
	let c = i ?? gt(e), l = _t(e), u = Math.min(100, Math.max(0, r));
	return /* @__PURE__ */ m("div", {
		role: "dialog",
		"aria-modal": mt(e) ? "true" : void 0,
		className: X("dialog-phone", `dialog-phone--${yt(e)}`, o),
		"data-type": e,
		...s,
		children: /* @__PURE__ */ h("div", {
			className: "dialog-phone__surface",
			children: [
				ft(e) ? /* @__PURE__ */ h("div", {
					className: X("dialog-phone__body", e === "title+content_2lines" && "dialog-phone__body--two-lines"),
					children: [/* @__PURE__ */ m("div", {
						className: X("dialog-phone__title-row", e === "title+content_2lines" && "dialog-phone__title-row--two-lines"),
						children: /* @__PURE__ */ m("h2", {
							className: "dialog-phone__title",
							children: t
						})
					}), /* @__PURE__ */ m("div", {
						className: X("dialog-phone__content", e === "title+content_single line" && "dialog-phone__content--single-line", e === "title+content_2lines" && "dialog-phone__content--two-lines"),
						children: /* @__PURE__ */ m("p", {
							className: "dialog-phone__content-text",
							children: n
						})
					})]
				}) : pt(e) && /* @__PURE__ */ m("div", {
					className: X("dialog-phone__content", e === "content+button" && "dialog-phone__content--single-line"),
					children: /* @__PURE__ */ m("p", {
						className: "dialog-phone__content-text",
						children: n
					})
				}),
				ht(e) && /* @__PURE__ */ h("div", {
					className: "dialog-phone__progress",
					children: [/* @__PURE__ */ h("div", {
						className: "dialog-phone__progress-meta",
						children: [/* @__PURE__ */ m("span", {
							className: "dialog-phone__progress-title",
							children: t
						}), /* @__PURE__ */ h("span", {
							className: "dialog-phone__progress-value",
							children: [Math.round(u), "%"]
						})]
					}), /* @__PURE__ */ h("div", {
						className: "dialog-phone__progress-track-row",
						children: [/* @__PURE__ */ m("div", {
							className: "dialog-phone__progress-track",
							"aria-hidden": "true",
							children: /* @__PURE__ */ m("div", {
								className: "dialog-phone__progress-fill",
								style: { width: `${u}%` }
							})
						}), /* @__PURE__ */ m("button", {
							type: "button",
							className: "dialog-phone__close",
							"aria-label": "Close",
							title: "Close",
							onClick: a,
							children: /* @__PURE__ */ m(vt, {})
						})]
					})]
				}),
				mt(e) && c.length > 0 && /* @__PURE__ */ m("div", {
					className: X("dialog-phone__button-group", `dialog-phone__button-group--${l}`),
					children: c.map((e) => /* @__PURE__ */ m("div", {
						className: "dialog-phone__button-item",
						children: /* @__PURE__ */ m("button", {
							type: "button",
							className: X("dialog-phone__button", e.variant === "emphasize" && "dialog-phone__button--emphasize"),
							"aria-label": e.label,
							onClick: e.onClick,
							children: e.label
						})
					}, e.id))
				})
			]
		})
	});
}
function xt({ open: e, onOpenChange: t, onClose: n, 内嵌: r, ...i }) {
	let a = () => {
		n?.(), t?.(!1);
	}, o = /* @__PURE__ */ m(bt, {
		...i,
		onClose: a
	});
	return e === void 0 ? o : e ? /* @__PURE__ */ h("div", {
		className: "dialog-phone-overlay",
		"data-container": r ? "true" : void 0,
		children: [/* @__PURE__ */ m("div", {
			className: "dialog-phone-overlay__backdrop",
			onClick: a,
			"aria-hidden": "true"
		}), o]
	}) : null;
}
//#endregion
//#region src/components/Container/DialogPhone/index.ts
var St = /* @__PURE__ */ _({
	DialogPhone: () => xt,
	DialogPhonePanel: () => bt,
	dialogPhoneTypes: () => dt
});
//#endregion
//#region src/lib/code2design.ts
function Ct(e, t) {
	let n = JSON.stringify({
		tagName: e,
		attributes: t
	}), r = new TextEncoder().encode(n), i = "";
	for (let e of r) i += String.fromCharCode(e);
	return `octoai-c2d-data-${btoa(i)}`;
}
var wt = typeof globalThis < "u" && globalThis.__C2D_BUILD__ === !0;
function Q(e, t) {
	if (!wt) return;
	let n = {};
	for (let [e, r] of Object.entries(t)) r != null && (n[e] = r);
	return Ct(e, n);
}
//#endregion
//#region src/components/Container/FloatingBindSheet/floating-bind-sheet.constants.ts
var Tt = ["标准"], Et = ["默认"], Dt = [!0, !1], Ot = [!0], kt = [
	149,
	434,
	748
];
function At(e, t) {
	return t.reduce((t, n) => Math.abs(n - e) < Math.abs(t - e) ? n : t, t[0]);
}
function jt(e, t) {
	let n = At(e, t);
	return t.findIndex((e) => e === n);
}
function Mt({ "Right icon": e = !0, Title: t, content: n = !0, 通透度: r = "标准", 状态: i = "默认", draggable: o = !1, defaultHeight: c = 240, minHeight: f = 160, maxHeight: p = 560, snapHeights: g, fixedToBottom: _ = !1, title: v = "Title", closeButtonLabel: y = "Close", onClose: b, onHeightChange: x, closeButtonProps: S, bgColor: C, children: w, className: T, style: E, ...D }) {
	let O = l(() => g?.length ? [...g].sort((e, t) => e - t) : void 0, [g]), k = O?.[0] ?? f, A = O?.[O.length - 1] ?? p, [j, M] = d(() => O ? At(c, O) : c), [N, P] = d(!1), F = u({
		currentHeight: c,
		height: c,
		pointerId: -1,
		startY: 0
	}), I = t ?? v, L = a((e) => Math.min(A, Math.max(k, e)), [A, k]), R = L(o ? j : c);
	s(() => {
		x?.(R);
	}, [x, R]);
	let z = a((e) => {
		o && (e.preventDefault(), F.current = {
			currentHeight: R,
			height: R,
			pointerId: e.pointerId,
			startY: e.clientY
		}, e.currentTarget.setPointerCapture(e.pointerId), P(!0));
	}, [o, R]), B = a((e) => {
		if (!o || F.current.pointerId !== e.pointerId) return;
		let t = F.current.startY - e.clientY, n = L(F.current.height + t);
		F.current.currentHeight = n, M(n);
	}, [L, o]), V = a((e) => {
		F.current.pointerId === e.pointerId && (e.currentTarget.hasPointerCapture(e.pointerId) && e.currentTarget.releasePointerCapture(e.pointerId), F.current.pointerId = -1, P(!1), O && M(At(F.current.currentHeight, O)));
	}, [L, O]), H = a((e) => {
		if (!o) return;
		let t;
		if (O) {
			let n = jt(R, O);
			e.key === "ArrowUp" || e.key === "PageUp" ? t = O[Math.min(n + 1, O.length - 1)] : e.key === "ArrowDown" || e.key === "PageDown" ? t = O[Math.max(n - 1, 0)] : e.key === "Home" ? t = O[0] : e.key === "End" && (t = O[O.length - 1]);
		} else {
			let n = e.shiftKey ? 40 : 16;
			e.key === "ArrowUp" || e.key === "PageUp" ? t = R + n : e.key === "ArrowDown" || e.key === "PageDown" ? t = R - n : e.key === "Home" ? t = k : e.key === "End" && (t = A);
		}
		t !== void 0 && (e.preventDefault(), M(L(t)));
	}, [
		L,
		o,
		R,
		O,
		A,
		k
	]);
	return /* @__PURE__ */ h("section", {
		className: X("pixso-floating-sheet hm-material-floating-ultra-thick", _ && "pixso-floating-sheet--fixed-bottom", o && "pixso-floating-sheet--draggable", N && "pixso-floating-sheet--dragging", Q("FloatingBindSheet", {
			通透度: r,
			状态: i,
			Title: I,
			"Right icon": e ? "true" : "false",
			content: n ? "true" : "false",
			draggable: o ? "true" : "false",
			defaultHeight: String(c),
			minHeight: String(f),
			maxHeight: String(p),
			height: String(R),
			...O?.length ? { snapHeights: O.join(",") } : {}
		}), T),
		"data-material": r,
		"data-state": i,
		"data-draggable": o ? "true" : "false",
		style: {
			"--floating-bind-sheet-height": `${R}px`,
			...C ? { "--floating-bind-sheet-bg": C } : {},
			...E
		},
		...D,
		children: [
			/* @__PURE__ */ m("button", {
				"aria-label": "Resize sheet",
				"aria-orientation": "vertical",
				"aria-valuemax": A,
				"aria-valuemin": k,
				"aria-valuenow": R,
				className: "pixso-floating-sheet__handle-row",
				disabled: !o,
				onPointerCancel: V,
				onPointerDown: z,
				onPointerMove: B,
				onPointerUp: V,
				onKeyDown: H,
				role: "slider",
				type: "button",
				children: /* @__PURE__ */ m("div", { className: "pixso-floating-sheet__handle" })
			}),
			/* @__PURE__ */ h("div", {
				className: "pixso-floating-sheet__header",
				children: [/* @__PURE__ */ m("h2", {
					className: "pixso-floating-sheet__title",
					children: I
				}), e ? /* @__PURE__ */ m("button", {
					"aria-label": y,
					className: "pixso-floating-sheet__close-button",
					onClick: b,
					type: "button",
					...S,
					children: /* @__PURE__ */ m(Pt, {})
				}) : null]
			}),
			n ? /* @__PURE__ */ m("div", {
				className: "pixso-floating-sheet__content",
				children: w ?? /* @__PURE__ */ m(Nt, {})
			}) : null
		]
	});
}
function Nt() {
	return /* @__PURE__ */ m("div", {
		className: "pixso-floating-sheet__placeholder",
		"aria-hidden": "true"
	});
}
function Pt() {
	return /* @__PURE__ */ m(Z, {
		className: "pixso-floating-sheet__close-icon",
		name: "xmark",
		size: 18
	});
}
//#endregion
//#region src/components/Container/FloatingBindSheet/index.ts
var Ft = /* @__PURE__ */ _({
	DEFAULT_SHEET_SNAP_HEIGHTS: () => kt,
	FloatingBindSheet: () => Mt,
	floatingBindSheetContentOptions: () => Ot,
	floatingBindSheetRightIconOptions: () => Dt,
	floatingBindSheet状态Options: () => Et,
	floatingBindSheet通透度Options: () => Tt
}), It = [
	"0.5",
	"1",
	"8"
], Lt = ["horizontal", "vertical"], Rt = ["solid", "dashed"];
function $({ 尺寸: e = "0.5", 方向: t = "horizontal", 样式: n = "solid", 颜色: r, className: i, style: a, ...o }) {
	let s = {
		...a,
		...r ? { "--hm-divider-color": r } : null
	};
	return /* @__PURE__ */ m("div", {
		className: X("hm-divider", `hm-divider--${t}`, `hm-divider--${e}`, `hm-divider--${n}`, i),
		style: s,
		...o
	});
}
//#endregion
//#region src/components/Views/Divider/index.ts
var zt = /* @__PURE__ */ _({
	Divider: () => $,
	hmDividerOrientations: () => Lt,
	hmDividerSizes: () => It,
	hmDividerVariants: () => Rt
}), Bt = [
	"content",
	"content+button",
	"title+content_single line",
	"title+content_2lines",
	"title+content+2 button",
	"title+content+3 button",
	"progress bar",
	"progress bar+button"
], Vt = ["标准"], Ht = ["on", "off"], Ut = [
	"normal",
	"emphasize",
	"emphasize-port"
], Wt = [
	1,
	2,
	3
], Gt = {
	content: 328,
	"content+button": 328,
	"title+content_single line": 328,
	"title+content_2lines": 328,
	"title+content+2 button": 328,
	"title+content+3 button": 328,
	"progress bar": 328,
	"progress bar+button": 299
}, Kt = "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA", qt = "AAAAAAAAAAAAAAAAAAAAAAAA";
function Jt({ 类型: e = "content", 通透度: t = "标准", mask: n = "off", 按钮组: r, 按钮组类型: i, 按钮组个数: a, className: o, style: s, ...c }) {
	let l = Gt[e], u = e.startsWith("title+content"), d = e === "title+content_2lines", f = e === "content" || e === "content+button" || e.startsWith("title+content"), g = e === "content+button", _ = e === "progress bar" || e === "progress bar+button", v = Xt(e), y = i ?? r?.类型 ?? "normal", b = a ?? r?.个数 ?? v;
	return /* @__PURE__ */ h(p, { children: [n === "on" ? /* @__PURE__ */ m("div", {
		className: "hm-floating-dialog__mask",
		"aria-hidden": "true"
	}) : null, /* @__PURE__ */ h("section", {
		className: X("hm-floating-dialog", "hm-material-floating-ultra-thick", Q("FloatingDialog", {
			类型: e,
			通透度: t
		}), o),
		"data-类型": e,
		"data-通透度": t,
		style: {
			"--hm-floating-dialog-width": `${l}px`,
			...s
		},
		...c,
		children: [
			u ? /* @__PURE__ */ h("div", {
				className: X("hm-floating-dialog__title-block", d && "hm-floating-dialog__title-block--with-auxiliary"),
				children: [/* @__PURE__ */ m("h3", {
					className: "hm-floating-dialog__title",
					children: "Title"
				}), d ? /* @__PURE__ */ m("p", {
					className: "hm-floating-dialog__auxiliary",
					children: "Auxiliary Text"
				}) : null]
			}) : null,
			f ? /* @__PURE__ */ m("p", {
				className: X("hm-floating-dialog__body", g && "hm-floating-dialog__body--single", !u && "hm-floating-dialog__body--content-only"),
				children: g ? qt : Kt
			}) : null,
			_ ? /* @__PURE__ */ m(en, {}) : null,
			Zt(b) ? /* @__PURE__ */ m(Yt, {
				类型: y,
				个数: b
			}) : null
		]
	})] });
}
function Yt({ 类型: e = "normal", 个数: t = 1 }) {
	let n = t, r = e === "normal" && n === 2;
	return e === "emphasize-port" ? /* @__PURE__ */ m("div", {
		className: "hm-floating-dialog__button-column",
		children: Array.from({ length: n }, (t, r) => /* @__PURE__ */ m($t, {
			tone: Qt(e, n, r),
			wide: !0
		}, r))
	}) : n === 1 ? /* @__PURE__ */ m("div", {
		className: "hm-floating-dialog__button-row hm-floating-dialog__button-row--single",
		children: /* @__PURE__ */ m($t, { tone: Qt(e, 1, 0) })
	}) : n === 2 ? /* @__PURE__ */ h("div", {
		className: "hm-floating-dialog__button-row hm-floating-dialog__button-row--two",
		children: [
			/* @__PURE__ */ m($t, { tone: Qt(e, 2, 0) }),
			r ? /* @__PURE__ */ m($, {
				方向: "vertical",
				尺寸: "1",
				颜色: "var(--harmony-comp-background-secondary)",
				className: "hm-floating-dialog__button-divider",
				"aria-hidden": "true"
			}) : null,
			/* @__PURE__ */ m($t, { tone: Qt(e, 2, 1) })
		]
	}) : /* @__PURE__ */ m("div", {
		className: "hm-floating-dialog__button-column",
		children: Array.from({ length: n }, (t, r) => /* @__PURE__ */ m($t, {
			tone: Qt(e, n, r),
			wide: !0
		}, r))
	});
}
function Xt(e) {
	switch (e) {
		case "content+button":
		case "progress bar+button": return 1;
		case "title+content+2 button": return 2;
		case "title+content+3 button": return 3;
		default: return 0;
	}
}
function Zt(e) {
	return e === 1 || e === 2 || e === 3;
}
function Qt(e, t, n) {
	switch (e) {
		case "normal": return "secondary";
		case "emphasize": return n === t - 1 ? "primary" : "secondary";
		case "emphasize-port": return n === 0 ? "primary" : "secondary";
		default: return "secondary";
	}
}
function $t({ tone: e, wide: t = !1 }) {
	return /* @__PURE__ */ m("button", {
		type: "button",
		className: X("hm-floating-dialog__button", `hm-floating-dialog__button--${e}`, t && "hm-floating-dialog__button--wide"),
		children: "BUTTON"
	});
}
function en() {
	return /* @__PURE__ */ h("div", {
		className: "hm-floating-dialog__progress",
		children: [/* @__PURE__ */ h("div", {
			className: "hm-floating-dialog__progress-header",
			children: [/* @__PURE__ */ m("span", {
				className: "hm-floating-dialog__progress-title",
				children: "Title"
			}), /* @__PURE__ */ m("span", {
				className: "hm-floating-dialog__progress-percent",
				children: "50%"
			})]
		}), /* @__PURE__ */ h("div", {
			className: "hm-floating-dialog__progress-row",
			children: [/* @__PURE__ */ m("div", {
				className: "hm-floating-dialog__track",
				children: /* @__PURE__ */ m("div", { className: "hm-floating-dialog__track-value" })
			}), /* @__PURE__ */ m("button", {
				type: "button",
				className: "hm-floating-dialog__close",
				"aria-label": "Close",
				children: /* @__PURE__ */ m("span", { "aria-hidden": "true" })
			})]
		})]
	});
}
//#endregion
//#region src/components/Container/FloatingDialog/index.ts
var tn = /* @__PURE__ */ _({
	FloatingDialog: () => Jt,
	FloatingDialogButtonGroup: () => Yt,
	floatingDialogButtonGroup个数Options: () => Wt,
	floatingDialogButtonGroup类型Options: () => Ut,
	floatingDialogMaskOptions: () => Ht,
	floatingDialogVariantWidthMap: () => Gt,
	floatingDialog类型Options: () => Bt,
	floatingDialog通透度Options: () => Vt
}), nn = ["Medium", "Small"], rn = [
	"Emphasized",
	"Normal",
	"Warning",
	"Text",
	"Selected",
	"Unselected"
], an = [
	"Enabled",
	"Hover",
	"Pressed",
	"Focus",
	"Loading",
	"Disabled"
], on = {
	"Medium-Text-Enabled": "TEXT BTN",
	"Medium-Text-Hover": "TEXT BTN",
	"Medium-Text-Pressed": "TEXT BTN",
	"Medium-Text-Focus": "TEXT BTN",
	"Medium-Text-Disabled": "TEXT BTN"
};
function sn({ 尺寸: e = "Medium", 类型: t = "Emphasized", 状态: n = "Enabled", children: r, className: i, ...a }) {
	let o = cn({
		size: e,
		type: t,
		state: n
	}), s = r ?? o, c = n === "Loading", l = e === "Medium" ? 24 : 16, u = n === "Disabled" || c, d = un({
		size: e,
		type: t
	}), f = t === "Text" && n === "Disabled";
	return /* @__PURE__ */ m("button", {
		type: "button",
		className: X("pixso-button", `pixso-button--${e.toLowerCase()}`, `pixso-button--type-${t}`, `pixso-button--state-${n}`, d, f && "pixso-button--text-disabled", i),
		"aria-disabled": u || void 0,
		disabled: u,
		"data-size": e,
		"data-type": t,
		"data-state": n,
		...a,
		children: /* @__PURE__ */ h("span", {
			className: "pixso-button__content",
			children: [c ? /* @__PURE__ */ m(dn, {
				size: l,
				className: "pixso-button__spinner"
			}) : null, /* @__PURE__ */ m("span", {
				className: "pixso-button__label",
				children: s
			})]
		})
	});
}
function cn({ size: e, type: t, state: n }) {
	return n === "Loading" ? "Loading" : on[`${e}-${t}-${n}`] ?? (e === "Small" ? "BTN" : "BUTTON");
}
function ln({ type: e }) {
	return e === "Selected" || e === "Unselected" ? "regular" : "medium";
}
function un({ size: e, type: t }) {
	let n = ln({ type: t });
	return e === "Medium" ? n === "regular" ? "pixso-button--font-regular pixso-button--line-medium-regular" : "pixso-button--font-medium pixso-button--line-medium" : n === "regular" ? "pixso-button--font-regular pixso-button--line-small" : "pixso-button--font-medium pixso-button--line-small";
}
function dn({ size: e, className: t, ...n }) {
	let r = fn(), i = e === 24 ? 2 : 1.3, a = e / 24 * 2.25, o = {
		centerX: 12,
		centerY: 12,
		radiusX: 13.1,
		radiusY: 6.7,
		rotationDeg: -45
	}, s = [
		1,
		.72,
		.5,
		.34,
		.2,
		.1
	].map((e, t) => pn({
		headRadius: a,
		index: t,
		opacity: e,
		orbit: o,
		progress: r,
		trailStep: .055
	})), c = s.filter((e) => e.depth <= 0), l = s.filter((e) => e.depth > 0);
	return /* @__PURE__ */ h("svg", {
		width: e,
		height: e,
		viewBox: "0 0 24 24",
		fill: "none",
		className: t,
		"aria-hidden": "true",
		...n,
		children: [
			c.map((e) => /* @__PURE__ */ m("circle", {
				cx: e.x,
				cy: e.y,
				r: e.radius,
				fill: "currentColor",
				opacity: e.opacity
			}, e.key)),
			/* @__PURE__ */ m("circle", {
				cx: "12",
				cy: "12",
				r: 8.75,
				stroke: "currentColor",
				strokeWidth: i
			}),
			l.map((e) => /* @__PURE__ */ m("circle", {
				cx: e.x,
				cy: e.y,
				r: e.radius,
				fill: "currentColor",
				opacity: e.opacity
			}, e.key))
		]
	});
}
function fn() {
	let [e, t] = d(0);
	return s(() => {
		if (typeof window > "u") return;
		let e = window.matchMedia("(prefers-reduced-motion: reduce)").matches ? 1800 : 1150, n = 0, r = performance.now(), i = (a) => {
			t((a - r) % e / e), n = window.requestAnimationFrame(i);
		};
		return n = window.requestAnimationFrame(i), () => window.cancelAnimationFrame(n);
	}, []), e;
}
function pn({ headRadius: e, index: t, opacity: n, orbit: r, progress: i, trailStep: a }) {
	let o = (i - t * a + 1) % 1 * Math.PI * 2, s = r.radiusX * Math.cos(o), c = r.radiusY * Math.sin(o), l = r.rotationDeg * Math.PI / 180, u = s * Math.cos(l) - c * Math.sin(l), d = s * Math.sin(l) + c * Math.cos(l), f = Math.sin(o), p = .68 + (f + 1) / 2 * .32;
	return {
		depth: f,
		key: t,
		opacity: n * (f > 0 ? 1 : .58),
		radius: e * p,
		x: r.centerX + u,
		y: r.centerY + d
	};
}
//#endregion
//#region src/components/Controls/Button/index.ts
var mn = /* @__PURE__ */ _({
	Button: () => sn,
	buttonSizes: () => nn,
	buttonStates: () => an,
	buttonTypes: () => rn
}), hn = ["phone"], gn = ["OFF", "ON"], _n = [
	"Enabled",
	"Hover",
	"Pressed",
	"Focus",
	"Disabled"
];
function vn({ type: e = "phone", Selected: t, defaultSelected: n = "OFF", 状态: r = "Enabled", className: i, disabled: o, onClick: s, ...c }) {
	let [l, u] = d(n), f = t !== void 0, p = f ? t : l, g = o || r === "Disabled", _ = a(() => {
		if (g) return;
		let e = p === "ON" ? "OFF" : "ON";
		s?.(e), f || u(e);
	}, [
		p,
		g,
		s,
		f
	]), v = `hm-checkbox--${e}`, y = p === "ON" ? "hm-checkbox--on" : "hm-checkbox--off", b = {
		Enabled: "hm-checkbox--enabled",
		Hover: "hm-checkbox--hover",
		Pressed: "hm-checkbox--pressed",
		Focus: "hm-checkbox--focus",
		Disabled: "hm-checkbox--disabled"
	}[r];
	return /* @__PURE__ */ h("button", {
		type: "button",
		className: X("hm-checkbox", v, y, b, i),
		disabled: g,
		role: "checkbox",
		"aria-checked": p === "ON",
		onClick: _,
		...c,
		children: [
			/* @__PURE__ */ m("span", {
				className: "hm-checkbox__box",
				children: p === "ON" && /* @__PURE__ */ m(Z, {
					className: "hm-checkbox__checkmark",
					name: "checkmark",
					size: 18,
					style: {
						color: "var(--checkbox-check-color)",
						height: 17
					}
				})
			}),
			r === "Hover" && /* @__PURE__ */ m("span", { className: "hm-checkbox__overlay hm-checkbox__overlay--hover" }),
			r === "Pressed" && /* @__PURE__ */ m("span", { className: "hm-checkbox__overlay hm-checkbox__overlay--pressed" })
		]
	});
}
//#endregion
//#region src/components/Selection/CheckBox/index.ts
var yn = /* @__PURE__ */ _({
	CheckBox: () => vn,
	checkBoxSelecteds: () => gn,
	checkBoxStates: () => _n,
	checkBoxTypes: () => hn
}), bn = ["OFF", "ON"], xn = [
	"Enabled",
	"Hover",
	"Focus",
	"Disabled"
];
function Sn({ Selected: e, defaultSelected: t = "OFF", 状态: n = "Enabled", className: r, disabled: i, onValueChange: a, onClick: o, ...s }) {
	let [c, l] = d(t), u = e !== void 0, f = u ? e : c, p = (e) => {
		let t = f === "ON" ? "OFF" : "ON";
		u || l(t), a?.(t), o?.(e);
	}, g = {
		OFF: "hm-radio-phone--off",
		ON: "hm-radio-phone--on"
	}[f], _ = {
		Enabled: "hm-radio-phone--enabled",
		Hover: "hm-radio-phone--hover",
		Focus: "hm-radio-phone--focus",
		Disabled: "hm-radio-phone--disabled"
	}[n];
	return /* @__PURE__ */ h("button", {
		...s,
		className: X("hm-radio-phone", g, _, r),
		disabled: i ?? n === "Disabled",
		role: "radio",
		"aria-checked": f === "ON",
		onClick: p,
		children: [/* @__PURE__ */ m("span", {
			className: "hm-radio-phone__outer",
			children: f === "ON" && /* @__PURE__ */ m(Z, {
				className: "hm-radio-phone__check",
				name: "checkmark",
				size: 18,
				style: {
					color: "var(--radio-phone-check-color)",
					height: 17
				}
			})
		}), n === "Hover" && /* @__PURE__ */ m("span", { className: "hm-radio-phone__hover-overlay" })]
	});
}
//#endregion
//#region src/components/Selection/RadioPhone/index.ts
var Cn = /* @__PURE__ */ _({
	RadioPhone: () => Sn,
	radioPhoneSelecteds: () => bn,
	radioPhoneStates: () => xn
}), wn = ["OFF", "ON"], Tn = [
	"Enabled",
	"Hover",
	"Pressed",
	"Focus",
	"Disabled"
];
function En({ Selected: e, defaultSelected: t = "OFF", 状态: n = "Enabled", className: r, disabled: i, onValueChange: a, onClick: o, ...s }) {
	let [c, l] = d(t), u = e !== void 0, f = u ? e : c, p = (e) => {
		let t = f === "ON" ? "OFF" : "ON";
		u || l(t), a?.(t), o?.(e);
	}, h = {
		OFF: "hm-switch-phone--off",
		ON: "hm-switch-phone--on"
	}[f], g = {
		Enabled: "hm-switch-phone--enabled",
		Hover: "hm-switch-phone--hover",
		Pressed: "hm-switch-phone--pressed",
		Focus: "hm-switch-phone--focus",
		Disabled: "hm-switch-phone--disabled"
	}[n];
	return /* @__PURE__ */ m("button", {
		...s,
		className: X("hm-switch-phone", h, g, r),
		disabled: i ?? n === "Disabled",
		role: "switch",
		"aria-checked": f === "ON",
		onClick: p,
		children: /* @__PURE__ */ m("span", { className: "hm-switch-phone__thumb" })
	});
}
//#endregion
//#region src/components/Selection/SwitchPhone/index.ts
var Dn = /* @__PURE__ */ _({
	SwitchPhone: () => En,
	switchPhoneSelecteds: () => wn,
	switchPhoneStates: () => Tn
}), On = [
	"1",
	"2",
	"3"
], kn = [
	"Text",
	"Dot",
	"8dp_ic",
	"16dp_ic",
	"24dp_ic",
	"40dp_ic",
	"48dp_ic",
	"badge",
	"badge longest",
	"Switch",
	"None"
], An = [
	"Text",
	"Dot",
	"24dp_ic",
	"40dp_ic",
	"48dp_ic",
	"16dp_ic",
	"second_16dp_ic",
	"badge",
	"badge longest",
	"Switch",
	"None"
], jn = [
	"默认",
	"Dot",
	"24dp_ic",
	"40dp_ic",
	"48dp_ic",
	"16dp_ic",
	"badge",
	"badge longest",
	"Switch",
	"None"
], Mn = [
	"Text",
	"Dot",
	"8dp_ic",
	"16dp_ic",
	"24dp_ic",
	"40dp_ic",
	"48dp_ic",
	"badge",
	"badge longest",
	"Switch",
	"None",
	"默认",
	"second_16dp_ic"
], Nn = {
	1: kn,
	2: An,
	3: jn
}, Pn = [
	"Menu select",
	"Text",
	"Arrow",
	"Radio",
	"Checkbox",
	"Switch",
	"Button",
	"Expand",
	"Icon",
	"2Icons",
	"8dp_ic",
	"image",
	"badge",
	"loading",
	"None"
], Fn = ["gearshape", "bookmark"], In = "gearshape", Ln = {
	S: 48,
	M: 56,
	L: 64,
	XL: 72,
	XXL: 96
};
function Rn({ 行数: e = "1", 尺寸: t, right: n = "Menu select", left: r, title: i = "Single list", subtitle: a, description: o, rightText: s, rightSubtitle: c, rightSelected: l, defaultRightSelected: u = "ON", onRightSelectedChange: d, onRightAction: f, onRightExpandedChange: p, rightDisabled: g = !1, rightExpanded: _ = !1, rightBadgeText: v = "New", rightImageSrc: y, rightImageAlt: b = "", rightIconGlyphs: x = Fn, leftText: S = "A", leftBadgeText: C = "1", leftSelected: w, defaultLeftSelected: T = "ON", onLeftSelectedChange: E, leftIconName: D = In, leftIconSize: O, leftIconColor: k, leftIconBackground: A, leftIconRadius: j, leftSlot: M, rightSlot: N, divider: P = !0, dividerMode: F = "content", dividerInsetStart: I, dividerInsetEnd: L, className: R, style: z, onClick: B, role: V, tabIndex: H, onKeyDown: ee, ...te }) {
	let U = r ?? er(e), ne = Jn(n), re = N != null && ne !== "icon", ie = ne === "expand", ae = M != null || U !== "Text" && U !== "None" && U !== "默认", oe = (e) => {
		ee?.(e), !(e.defaultPrevented || e.currentTarget !== e.target) && (e.key === "Enter" || e.key === " ") && B && (e.preventDefault(), B());
	}, se = M == null ? Bn({
		defaultLeftSelected: T,
		left: U,
		leftBadgeText: C,
		leftIconName: D,
		leftIconSize: O,
		leftSelected: w,
		leftText: S,
		onLeftSelectedChange: E
	}) : /* @__PURE__ */ m("span", {
		className: "list-phone__left-addon list-phone__left-slot",
		"data-list-phone-left-kind": "custom",
		children: M
	}), ce = {
		...z,
		...t ? { "--list-row-height": `${Ln[t]}px` } : null,
		"--list-left-addon-width": `${Xn(U, M != null)}px`,
		"--list-left-addon-gap": ae ? "12px" : "0px",
		...k === void 0 ? null : { "--list-left-icon-color": k },
		...A === void 0 ? null : { "--list-left-icon-background": A },
		...j === void 0 ? null : { "--list-left-icon-radius": Zn(j) },
		...I === void 0 ? null : { "--list-divider-inset-start": Zn(I) },
		...L === void 0 ? null : { "--list-divider-inset-end": Zn(L) }
	};
	return /* @__PURE__ */ h("div", {
		role: V ?? (B ? "button" : "listitem"),
		tabIndex: H ?? (B ? 0 : void 0),
		className: X("list-phone", `list-phone--lines-${e}`, `list-phone--right-${ne}`, ae && "list-phone--with-left-addon", R),
		style: ce,
		"data-component": "ListPhone",
		"data-lines": e,
		"data-left": U,
		"data-right": n,
		"data-right-kind": ne,
		"data-divider": P ? "show" : "hide",
		"data-divider-mode": F,
		"data-size": t ?? null,
		"aria-expanded": ie ? _ : void 0,
		onClick: B,
		onKeyDown: oe,
		...te,
		children: [se, /* @__PURE__ */ h("div", {
			className: "list-phone__main",
			"data-list-phone-region": "main",
			children: [zn({
				description: o,
				lines: e,
				subtitle: a,
				title: i
			}), re ? N : Vn({
				rightBadgeText: v,
				defaultRightSelected: u,
				onRightAction: f,
				onRightExpandedChange: p,
				onRightSelectedChange: d,
				rightDisabled: g,
				rightExpanded: _,
				rightIconGlyphs: x,
				rightImageAlt: b,
				rightImageSrc: y,
				rightKind: ne,
				rightSelected: l,
				rightSubtitle: c,
				rightText: s
			})]
		})]
	});
}
function zn({ description: e, lines: t, subtitle: n, title: r }) {
	return /* @__PURE__ */ h("div", {
		className: "list-phone__content list-phone__left",
		"data-list-phone-region": "content",
		children: [
			/* @__PURE__ */ m("span", {
				className: "list-phone__title",
				"data-list-phone-line": "title",
				children: r
			}),
			t !== "1" && n ? /* @__PURE__ */ m("span", {
				className: "list-phone__subtitle",
				"data-list-phone-line": "subtitle",
				children: n
			}) : null,
			t === "3" && e ? /* @__PURE__ */ m("span", {
				className: "list-phone__description",
				"data-list-phone-line": "description",
				children: e
			}) : null
		]
	});
}
function Bn({ defaultLeftSelected: e, left: t, leftBadgeText: n, leftIconName: r, leftIconSize: i, leftSelected: a, leftText: o, onLeftSelectedChange: s }) {
	if (t === "Text" || t === "None" || t === "默认") return null;
	if (t === "Dot") return /* @__PURE__ */ m("span", {
		className: "list-phone__left-addon",
		"data-list-phone-left-kind": "dot",
		"aria-hidden": "true",
		children: /* @__PURE__ */ m("span", { className: "list-phone__dot" })
	});
	if (t === "badge" || t === "badge longest") return /* @__PURE__ */ m("span", {
		className: "list-phone__left-addon",
		"data-list-phone-left-kind": "badge",
		children: /* @__PURE__ */ m(Kn, { children: t === "badge longest" ? "Badge" : n })
	});
	if (t === "Switch") return /* @__PURE__ */ m("span", {
		className: "list-phone__left-addon list-phone__control-wrap",
		"data-list-phone-left-kind": "switch",
		onClick: (e) => e.stopPropagation(),
		children: /* @__PURE__ */ m(En, {
			Selected: a === void 0 ? void 0 : Qn(a),
			defaultSelected: Qn(e),
			onValueChange: s,
			"aria-label": "Left switch"
		})
	});
	let c = Yn(t), l = c <= 16;
	return /* @__PURE__ */ m("span", {
		className: X("list-phone__left-addon", "list-phone__left-icon", l && "list-phone__left-icon--mini"),
		"data-list-phone-left-kind": "icon",
		"data-list-phone-left-size": c,
		"aria-hidden": "true",
		children: l ? /* @__PURE__ */ m("span", {
			className: "list-phone__mini-mark",
			children: o
		}) : /* @__PURE__ */ m(Z, {
			name: r,
			size: i ?? Math.min(c, 24)
		})
	});
}
function Vn({ rightBadgeText: e, defaultRightSelected: t, onRightAction: n, onRightExpandedChange: r, onRightSelectedChange: i, rightDisabled: a, rightExpanded: o, rightIconGlyphs: s, rightImageAlt: c, rightImageSrc: l, rightKind: u, rightSelected: d, rightSubtitle: f, rightText: p }) {
	let g = d === void 0 ? void 0 : Qn(d), _ = Qn(t), v = () => {
		n?.();
	}, y = () => {
		r?.(!o), n?.();
	};
	return /* @__PURE__ */ m("div", {
		className: "list-phone__right",
		"data-list-phone-region": "right",
		children: (() => {
			switch (u) {
				case "menu-select": return /* @__PURE__ */ h(Gn, {
					ariaLabel: "Open menu",
					disabled: a,
					onAction: n ? v : void 0,
					children: [/* @__PURE__ */ m(Hn, { value: p }), /* @__PURE__ */ m(Un, {
						direction: "down",
						label: "Open menu"
					})]
				});
				case "text": return /* @__PURE__ */ m(Hn, { value: p });
				case "arrow": return /* @__PURE__ */ h(Gn, {
					ariaLabel: "Open details",
					disabled: a,
					onAction: n ? v : void 0,
					children: [$n(p) ? /* @__PURE__ */ m(Hn, { value: p }) : null, /* @__PURE__ */ m(Un, {
						direction: "right",
						label: "Open details"
					})]
				});
				case "radio": return /* @__PURE__ */ m(Wn, { children: /* @__PURE__ */ m(Sn, {
					Selected: g,
					defaultSelected: _,
					disabled: a,
					onValueChange: i,
					"aria-label": "Select row"
				}) });
				case "checkbox": return /* @__PURE__ */ m(Wn, { children: /* @__PURE__ */ m(vn, {
					Selected: g,
					defaultSelected: _,
					disabled: a,
					onClick: i,
					"aria-label": "Check row"
				}) });
				case "switch": return /* @__PURE__ */ m(Wn, { children: /* @__PURE__ */ m(En, {
					Selected: g,
					defaultSelected: _,
					disabled: a,
					onValueChange: i,
					"aria-label": "Toggle row"
				}) });
				case "button": return /* @__PURE__ */ m(Wn, { children: /* @__PURE__ */ m(sn, {
					尺寸: "Small",
					类型: "Normal",
					状态: a ? "Disabled" : "Enabled",
					onClick: n,
					"aria-label": String(p || "Action"),
					children: $n(p) ? p : void 0
				}) });
				case "expand": return /* @__PURE__ */ h(Gn, {
					ariaExpanded: o,
					ariaLabel: o ? "Collapse row" : "Expand row",
					disabled: a,
					onAction: r || n ? y : void 0,
					children: [/* @__PURE__ */ h("span", {
						className: "list-phone__right-two-line",
						children: [/* @__PURE__ */ m(Hn, { value: p }), /* @__PURE__ */ m("span", {
							className: "list-phone__right-subtext",
							children: f ?? "More detail"
						})]
					}), /* @__PURE__ */ m(Un, {
						direction: o ? "up" : "right",
						label: o ? "Collapse row" : "Expand row"
					})]
				});
				case "icon": return /* @__PURE__ */ m(Gn, {
					ariaLabel: "Icon action",
					disabled: a,
					onAction: n ? v : void 0,
					children: /* @__PURE__ */ m("span", {
						className: "list-phone__icon-set",
						children: /* @__PURE__ */ m(Z, {
							name: s[0] ?? "gearshape",
							size: 24
						})
					})
				});
				case "icon-arrow": return /* @__PURE__ */ h(Gn, {
					ariaLabel: "Open details",
					disabled: a,
					onAction: n ? v : void 0,
					children: [/* @__PURE__ */ m("span", {
						className: "list-phone__icon-set",
						children: /* @__PURE__ */ m(Z, {
							name: s[0] ?? "gearshape",
							size: 24
						})
					}), /* @__PURE__ */ m(Un, {
						direction: "right",
						label: "Open details"
					})]
				});
				case "two-icons": return /* @__PURE__ */ m(Gn, {
					ariaLabel: "Icon actions",
					disabled: a,
					onAction: n ? v : void 0,
					children: /* @__PURE__ */ m("span", {
						className: "list-phone__icon-set",
						children: s.slice(0, 2).map((e, t) => /* @__PURE__ */ m(Z, {
							name: e,
							size: 24
						}, t))
					})
				});
				case "image": return /* @__PURE__ */ m(qn, {
					alt: c,
					src: l
				});
				case "badge": return /* @__PURE__ */ h(Gn, {
					ariaLabel: "Open details",
					disabled: a,
					onAction: n ? v : void 0,
					children: [/* @__PURE__ */ m(Kn, { children: e }), /* @__PURE__ */ m(Un, {
						direction: "right",
						label: "Open details"
					})]
				});
				case "loading": return /* @__PURE__ */ m("span", {
					className: "list-phone__spinner",
					"aria-label": "Loading",
					role: "status"
				});
				case "none": return null;
			}
		})()
	});
}
function Hn({ value: e }) {
	return /* @__PURE__ */ m("span", {
		className: "list-phone__right-text",
		"data-list-phone-right-text": "true",
		children: e
	});
}
function Un({ direction: e, label: t }) {
	return e === "down" ? /* @__PURE__ */ m("span", {
		className: "list-phone__chevron",
		"aria-label": t,
		role: "img",
		style: { color: "var(--harmony-icon-tertiary)" },
		children: /* @__PURE__ */ m(Z, {
			name: "arrowtriangle_down_fill",
			size: 14
		})
	}) : e === "up" ? /* @__PURE__ */ m("span", {
		className: "list-phone__chevron",
		"aria-label": t,
		role: "img",
		children: /* @__PURE__ */ m(Z, {
			name: "arrowtriangle_up_fill",
			size: 14
		})
	}) : /* @__PURE__ */ m("span", {
		className: "list-phone__chevron list-phone__chevron--arrow",
		"aria-label": t,
		role: "img",
		children: /* @__PURE__ */ m(Z, {
			name: "chevron_right",
			size: 24,
			style: { width: 12 }
		})
	});
}
function Wn({ children: e }) {
	return /* @__PURE__ */ m("span", {
		className: "list-phone__control-wrap",
		"data-list-phone-control": "true",
		onClick: (e) => e.stopPropagation(),
		onKeyDown: (e) => e.stopPropagation(),
		children: e
	});
}
function Gn({ ariaExpanded: e, ariaLabel: t, children: n, disabled: r = !1, onAction: i }) {
	let a = !!i && !r;
	return /* @__PURE__ */ m("span", {
		"aria-disabled": r || void 0,
		"aria-expanded": e,
		"aria-label": t,
		className: "list-phone__action-wrap",
		"data-list-phone-action": a ? "true" : "false",
		onClick: (e) => {
			!i && !r || (e.stopPropagation(), a && i?.());
		},
		onKeyDown: (e) => {
			!a || e.key !== "Enter" && e.key !== " " || (e.stopPropagation(), e.preventDefault(), i?.());
		},
		role: a ? "button" : void 0,
		tabIndex: a ? 0 : void 0,
		children: n
	});
}
function Kn({ children: e }) {
	return /* @__PURE__ */ m("span", {
		className: "list-phone__badge",
		children: e
	});
}
function qn({ alt: e, src: t }) {
	return t ? /* @__PURE__ */ m("img", {
		className: "list-phone__image",
		src: t,
		alt: e
	}) : /* @__PURE__ */ m("span", {
		className: "list-phone__image list-phone__image--placeholder",
		role: "img",
		"aria-label": e || "Image",
		children: /* @__PURE__ */ m(Z, {
			name: "picture_fill",
			size: 18
		})
	});
}
function Jn(e) {
	switch (e) {
		case "Menu select": return "menu-select";
		case "Text": return "text";
		case "Arrow": return "arrow";
		case "Radio": return "radio";
		case "Checkbox": return "checkbox";
		case "Switch": return "switch";
		case "Button": return "button";
		case "Expand": return "expand";
		case "Icon": return "icon";
		case "8dp_ic": return "icon-arrow";
		case "2Icons": return "two-icons";
		case "image": return "image";
		case "badge": return "badge";
		case "loading": return "loading";
		case "None": return "none";
	}
}
function Yn(e) {
	switch (e) {
		case "8dp_ic": return 8;
		case "16dp_ic": return 16;
		case "24dp_ic": return 24;
		case "40dp_ic": return 40;
		case "48dp_ic": return 48;
		default: return 24;
	}
}
function Xn(e, t) {
	return t || e === "Text" || e === "None" || e === "默认" ? 0 : e === "Dot" ? 8 : e === "badge" ? 18 : e === "badge longest" ? 46 : e === "Switch" ? 40 : Yn(e);
}
function Zn(e) {
	return typeof e == "number" ? `${e}px` : e;
}
function Qn(e) {
	return e === !0 || e === "ON" ? "ON" : "OFF";
}
function $n(e) {
	return e == null || e === !1 ? !1 : typeof e == "string" ? e.trim().length > 0 : Array.isArray(e) ? e.length > 0 : !0;
}
function er(e) {
	return e === "3" ? "默认" : "Text";
}
function tr(e, t) {
	return Nn[e].includes(t);
}
//#endregion
//#region src/components/Container/ListPhone/index.ts
var nr = /* @__PURE__ */ _({
	ListPhone: () => Rn,
	isValidLeftForLines: () => tr,
	listPhoneLeftOptionsByLines: () => Nn,
	listPhoneLeftTypes: () => Mn,
	listPhoneLine1LeftTypes: () => kn,
	listPhoneLine2LeftTypes: () => An,
	listPhoneLine3LeftTypes: () => jn,
	listPhoneLines: () => On,
	listPhoneRightTypes: () => Pn
}), rr = [
	"Left",
	"Right",
	"Up",
	"Down"
], ir = [
	"1",
	"2",
	"3"
];
function ar({ 方向: e = "Up", 箭头: t = "1", arrow: n = !0, glass: r = !0, children: i, className: a, ...o }) {
	return /* @__PURE__ */ h("div", {
		className: X("popup", !n && "popup--no-arrow", !r && "popup--no-glass", a),
		...o,
		children: [
			/* @__PURE__ */ m("div", { className: "popup__bg" }),
			n && /* @__PURE__ */ m("div", { className: X("popup__arrow", `popup__arrow--${e.toLowerCase()}`, `popup__arrow--pos-${t}`) }),
			/* @__PURE__ */ m("div", {
				className: "popup__content",
				children: i
			})
		]
	});
}
//#endregion
//#region src/components/Container/Popup/index.ts
var or = /* @__PURE__ */ _({
	Popup: () => ar,
	PopupArrowPositions: () => ir,
	PopupDirections: () => rr
}), sr = [
	"hm-material-style-layer-floating-thin-fill-1",
	"hm-material-style-layer-floating-thin-fill-2",
	"hm-material-style-layer-floating-thin-effect-1",
	"hm-material-style-layer-floating-thin-effect-3",
	"hm-material-style-layer-floating-thin-effect-4",
	"hm-material-style-layer-floating-thin-effect-5",
	"hm-material-style-layer-floating-thin-effect-6",
	"hm-material-style-layer-floating-thin-effect-7",
	"hm-material-style-layer-floating-thin-effect-8"
], cr = ["ON", "OFF"], lr = ["3", "5"], ur = [
	"标准",
	"强",
	"弱"
], dr = {
	play: "play_fill",
	stopwatch: "stopwatch",
	voice: "mic_fill"
};
function fr(e) {
	return e === "5" ? [
		{
			id: "stopwatch-leading",
			icon: dr.stopwatch,
			label: "Stopwatch"
		},
		{
			id: "stopwatch-secondary",
			icon: dr.stopwatch,
			label: "Stopwatch"
		},
		{
			id: "play",
			icon: dr.play,
			label: "Play",
			primary: !0,
			activeIcon: "pause"
		},
		{
			id: "voice-secondary",
			icon: dr.voice,
			label: "Voice"
		},
		{
			id: "voice-trailing",
			icon: dr.voice,
			label: "Voice"
		}
	] : [
		{
			id: "stopwatch",
			icon: dr.stopwatch,
			label: "Stopwatch"
		},
		{
			id: "play",
			icon: dr.play,
			label: "Play",
			primary: !0,
			activeIcon: "pause"
		},
		{
			id: "voice",
			icon: dr.voice,
			label: "Voice"
		}
	];
}
function pr({ Port: e = "OFF", 个数: t = "3", 浮动: n = !1, 通透度: r = "标准", actions: i, activeActionId: a, defaultActiveActionId: o, onActionClick: s, className: c }) {
	return n ? /* @__PURE__ */ m(mr, {
		Port: e,
		个数: t,
		通透度: r,
		actions: i,
		activeActionId: a,
		defaultActiveActionId: o,
		onActionClick: s,
		className: c
	}) : /* @__PURE__ */ m(hr, {
		Port: e,
		个数: t,
		actions: i,
		activeActionId: a,
		defaultActiveActionId: o,
		onActionClick: s,
		className: c,
		floating: !1
	});
}
function mr({ Port: e = "OFF", 个数: t = "3", 通透度: n = "标准", actions: r, activeActionId: i, defaultActiveActionId: a, onActionClick: o, className: s }) {
	return /* @__PURE__ */ m(hr, {
		Port: e,
		个数: t,
		通透度: n,
		actions: r,
		activeActionId: i,
		defaultActiveActionId: a,
		onActionClick: o,
		className: s,
		floating: !0
	});
}
function hr({ Port: e, 个数: t, 通透度: n, actions: r, activeActionId: i, defaultActiveActionId: a, onActionClick: o, className: s, floating: c }) {
	let [l, u] = d(a), f = r && r.length > 0 ? r : fr(t), p = i ?? l, g = c && n === "标准";
	return /* @__PURE__ */ m("div", {
		className: X("pixso-actionbar", c && "pixso-actionbar--floating", s),
		"data-port": e,
		"data-count": t,
		"data-transparency": c ? n : void 0,
		children: /* @__PURE__ */ h("div", {
			className: X("pixso-actionbar__surface", g && "hm-material-style-layer-floating-thin-effect-2"),
			children: [g ? sr.map((e) => /* @__PURE__ */ m("span", { className: X("hm-material-style-layer", e) }, e)) : null, f.map((e) => /* @__PURE__ */ m(gr, {
				action: e,
				active: e.id === p,
				useActiveIcon: !c,
				onActionClick: (e) => {
					u(e.id === p ? void 0 : e.id), e.onClick?.(), o?.(e);
				}
			}, e.id))]
		})
	});
}
function gr({ action: e, active: t, useActiveIcon: n = !0, onActionClick: r }) {
	return /* @__PURE__ */ m("button", {
		type: "button",
		className: X("pixso-actionbar__item", e.primary ? "pixso-actionbar__item--primary" : "pixso-actionbar__item--standard"),
		"data-active": t ? "true" : void 0,
		"aria-label": e.label,
		"aria-pressed": t,
		disabled: e.disabled,
		title: e.label,
		onClick: () => r(e),
		children: /* @__PURE__ */ m(Z, {
			name: t && n && e.activeIcon ? e.activeIcon : e.icon,
			size: 24
		})
	});
}
//#endregion
//#region src/components/Controls/ActionBar/index.ts
var _r = /* @__PURE__ */ _({
	ActionBar: () => pr,
	FloatingActionBar: () => mr,
	actionBarCounts: () => lr,
	actionBarPorts: () => cr,
	actionBarTransparencies: () => ur
}), vr = [
	"Enabled",
	"Hover",
	"Pressed",
	"Focus",
	"Disabled"
];
function yr({ className: e }) {
	return /* @__PURE__ */ m(Z, {
		className: X("chips__icon-svg", e),
		name: "star",
		size: 16
	});
}
function br({ className: e }) {
	return /* @__PURE__ */ m(Z, {
		className: X("chips__close-svg", e),
		name: "xmark",
		size: 16
	});
}
function xr({ Close: e = !0, icon: t = !0, 状态: n, children: r = "Tabs", iconElement: i, className: a, disabled: o, closeLabel: s = "Remove", onClose: c, onClick: l, ...u }) {
	let d = n === "Disabled" || o, f = (e) => {
		e.stopPropagation(), c?.();
	};
	return /* @__PURE__ */ h("button", {
		type: "button",
		disabled: d,
		className: X("chips", a),
		"data-state": n ?? (d ? "Disabled" : "Enabled"),
		"data-close": e,
		"data-icon": t,
		"aria-disabled": d || void 0,
		onClick: d ? void 0 : l,
		...u,
		children: [
			t ? /* @__PURE__ */ m("span", {
				className: "chips__icon",
				"aria-hidden": "true",
				children: i ?? /* @__PURE__ */ m(yr, {})
			}) : null,
			/* @__PURE__ */ m("span", {
				className: "chips__text",
				children: r
			}),
			e ? /* @__PURE__ */ m("span", {
				className: "chips__close",
				role: "button",
				tabIndex: d ? -1 : 0,
				"aria-label": s,
				onClick: d ? void 0 : f,
				onKeyDown: (e) => {
					(e.key === "Enter" || e.key === " ") && (e.preventDefault(), e.stopPropagation(), d || f(e));
				},
				children: /* @__PURE__ */ m(br, {})
			}) : null
		]
	});
}
//#endregion
//#region src/components/Controls/Chips/index.ts
var Sr = /* @__PURE__ */ _({
	Chips: () => xr,
	chipsStates: () => vr
}), Cr = /* @__PURE__ */ _({
	FloatingActionBar: () => mr,
	floatingActionBarCounts: () => lr,
	floatingActionBarPorts: () => cr,
	floatingActionBarTransparencies: () => ur
}), wr = ["Medium", "Small"], Tr = [
	"Emphasized",
	"Normal",
	"Warning",
	"Selected",
	"Unselected"
], Er = [
	"Enabled",
	"Hover",
	"Pressed",
	"Focus",
	"Loading",
	"Disabled"
], Dr = [
	"标准",
	"强",
	"降档",
	"弱"
], Or = ["hm-material-style-layer-floating-thin-fill-1", "hm-material-style-layer-floating-thin-fill-2"], kr = [
	"hm-material-style-layer-floating-thin-effect-1",
	"hm-material-style-layer-floating-thin-effect-3",
	"hm-material-style-layer-floating-thin-effect-4",
	"hm-material-style-layer-floating-thin-effect-5",
	"hm-material-style-layer-floating-thin-effect-6",
	"hm-material-style-layer-floating-thin-effect-7",
	"hm-material-style-layer-floating-thin-effect-8"
], Ar = [...Or, ...kr];
function jr(e) {
	return e === "Emphasized" || e === "Selected";
}
function Mr({ 尺寸: e = "Medium", 类型: t = "Emphasized", 状态: n = "Enabled", 通透度: r = "弱", children: i, className: a, navigateTo: o, 导航目标: s, onClick: c, onNavigate: l, ...u }) {
	let d = n === "Disabled" || n === "Loading", f = n === "Loading", p = f ? Pr({
		size: e,
		state: n
	}) : i ?? Pr({
		size: e,
		state: n
	}), g = o ?? s, _ = Nr(r), v = r === "标准" && !jr(t);
	return /* @__PURE__ */ h("button", {
		type: "button",
		className: X("hm-floating-button-phone", `hm-floating-button-phone--${e.toLowerCase()}`, `hm-floating-button-phone--type-${t}`, `hm-floating-button-phone--state-${n}`, _, v && "hm-material-style-layer-floating-thin-effect-2", a),
		"aria-disabled": d || void 0,
		"data-size": e,
		"data-state": n,
		"data-type": t,
		"data-opacity": r,
		"data-navigation-target": g,
		disabled: d,
		onClick: (e) => {
			if (c?.(e), e.defaultPrevented || d || !g || (l?.(g, e), e.defaultPrevented || typeof window > "u")) return;
			let t = new CustomEvent("hm:navigate", {
				bubbles: !0,
				cancelable: !0,
				detail: {
					source: "FloatingButtonPhone",
					target: g
				}
			});
			e.currentTarget.dispatchEvent(t);
		},
		...u,
		children: [v ? Ar.map((e) => /* @__PURE__ */ m("span", { className: X("hm-material-style-layer", e) }, e)) : null, /* @__PURE__ */ h("span", {
			className: "hm-floating-button-phone__content",
			children: [f && /* @__PURE__ */ m("svg", {
				className: "hm-floating-button-phone__spinner",
				viewBox: "0 0 26 24",
				fill: "none",
				"aria-hidden": "true",
				children: /* @__PURE__ */ h("g", {
					fill: "currentColor",
					children: [
						/* @__PURE__ */ m("path", {
							d: "M23.5 12C23.5 7.02944 19.4706 3 14.5 3C9.52944 3 5.5 7.02944 5.5 12C5.5 16.9706 9.52944 21 14.5 21C19.4706 21 23.5 16.9706 23.5 12ZM21.5 12C21.5 8.13401 18.366 5 14.5 5C10.634 5 7.5 8.13401 7.5 12C7.5 15.866 10.634 19 14.5 19C18.366 19 21.5 15.866 21.5 12Z",
							fillRule: "evenodd"
						}),
						/* @__PURE__ */ m("circle", {
							cx: "2.5",
							cy: "14.5",
							r: "2"
						}),
						/* @__PURE__ */ m("circle", {
							cx: "2",
							cy: "15",
							r: "2"
						})
					]
				})
			}), /* @__PURE__ */ m("span", {
				className: "hm-floating-button-phone__label",
				children: p
			})]
		})]
	});
}
function Nr(e) {
	switch (e) {
		case "标准": return "hm-floating-button-phone--opacity-standard";
		case "强": return "hm-floating-button-phone--opacity-strong";
		case "降档": return "hm-floating-button-phone--opacity-downshift";
		case "弱": return "hm-floating-button-phone--opacity-weak";
	}
}
function Pr({ size: e, state: t }) {
	return t === "Loading" ? "Loading" : e === "Medium" ? "BUTTON" : "BTN";
}
//#endregion
//#region src/components/Controls/FloatingButtonPhone/index.ts
var Fr = /* @__PURE__ */ _({
	FloatingButtonPhone: () => Mr,
	floatingButtonPhoneOpacities: () => Dr,
	floatingButtonPhoneSizes: () => wr,
	floatingButtonPhoneStates: () => Er,
	floatingButtonPhoneTypes: () => Tr
});
//#endregion
//#region src/components/Controls/FloatingChips/FloatingChips.tsx
function Ir({ className: e }) {
	return /* @__PURE__ */ m(Z, {
		className: X("hm-floating-chips__icon-svg", e),
		name: "star",
		size: 16
	});
}
function Lr({ className: e }) {
	return /* @__PURE__ */ m(Z, {
		className: X("hm-floating-chips__close-svg", e),
		name: "xmark",
		size: 16
	});
}
function Rr({ Close: e = !0, icon: t = !0, 状态: n = "Enabled", 通透度: r = "标准", children: i = "Tabs", iconElement: a, className: o, disabled: s, closeLabel: c = "Remove", onClose: l, onClick: u, ...d }) {
	let f = s ? "Disabled" : n, p = f === "Disabled", g = (e) => {
		e.stopPropagation(), l?.();
	};
	return /* @__PURE__ */ h("button", {
		"aria-disabled": p || void 0,
		className: X("hm-floating-chips", "hm-material-style-layer-floating-ultra-thin-effect-2", Q("FloatingChips", {
			Close: String(e),
			icon: String(t),
			状态: f,
			通透度: r
		}), o),
		"data-close": e,
		"data-icon": t,
		"data-opacity": r,
		"data-state": f,
		disabled: p,
		onClick: p ? void 0 : u,
		type: "button",
		...d,
		children: [
			/* @__PURE__ */ m("div", { className: "hm-material-style-layer hm-material-style-layer-floating-ultra-thin-fill-1" }),
			/* @__PURE__ */ m("div", { className: "hm-material-style-layer hm-material-style-layer-floating-ultra-thin-fill-2" }),
			/* @__PURE__ */ m("div", { className: "hm-material-style-layer hm-material-style-layer-floating-ultra-thin-effect-1" }),
			/* @__PURE__ */ m("div", { className: "hm-material-style-layer hm-material-style-layer-floating-ultra-thin-effect-3" }),
			/* @__PURE__ */ m("div", { className: "hm-material-style-layer hm-material-style-layer-floating-ultra-thin-effect-4" }),
			/* @__PURE__ */ m("div", { className: "hm-material-style-layer hm-material-style-layer-floating-ultra-thin-effect-5" }),
			/* @__PURE__ */ m("div", { className: "hm-material-style-layer hm-material-style-layer-floating-ultra-thin-effect-6" }),
			/* @__PURE__ */ m("div", { className: "hm-material-style-layer hm-material-style-layer-floating-ultra-thin-effect-7" }),
			/* @__PURE__ */ m("div", { className: "hm-material-style-layer hm-material-style-layer-floating-ultra-thin-effect-8" }),
			/* @__PURE__ */ h("span", {
				className: "hm-floating-chips__content",
				children: [
					t ? /* @__PURE__ */ m("span", {
						"aria-hidden": "true",
						className: "hm-floating-chips__icon",
						children: a ?? /* @__PURE__ */ m(Ir, {})
					}) : null,
					/* @__PURE__ */ m("span", {
						className: "hm-floating-chips__text",
						children: i
					}),
					e ? /* @__PURE__ */ m("span", {
						"aria-label": c,
						className: "hm-floating-chips__close",
						onClick: p ? void 0 : g,
						onKeyDown: (e) => {
							(e.key === "Enter" || e.key === " ") && (e.preventDefault(), e.stopPropagation(), p || l?.());
						},
						role: "button",
						tabIndex: p ? -1 : 0,
						children: /* @__PURE__ */ m(Lr, {})
					}) : null
				]
			})
		]
	});
}
//#endregion
//#region src/components/Controls/FloatingChips/index.ts
var zr = /* @__PURE__ */ _({
	FloatingChips: () => Rr,
	default: () => Rr
}), Br = [
	"hm-material-style-layer-floating-thick-fill-1",
	"hm-material-style-layer-floating-thick-fill-2",
	"hm-material-style-layer-floating-thick-effect-2",
	"hm-material-style-layer-floating-thick-effect-3",
	"hm-material-style-layer-floating-thick-effect-4",
	"hm-material-style-layer-floating-thick-effect-5",
	"hm-material-style-layer-floating-thick-effect-6",
	"hm-material-style-layer-floating-thick-effect-7",
	"hm-material-style-layer-floating-thick-effect-8"
], Vr = [
	1,
	2,
	3,
	4,
	5,
	6
], Hr = [
	"弱",
	"标准",
	"降档",
	"高"
], Ur = [
	"collapse",
	"commence",
	"selected"
], Wr = "segmented_button_highlight";
function Gr() {
	return /* @__PURE__ */ m(Z, {
		name: "chevron_right",
		size: 24
	});
}
function Kr() {
	return /* @__PURE__ */ m(Z, {
		name: "chevron_down",
		size: 24
	});
}
function qr() {
	return /* @__PURE__ */ m(Z, {
		name: "checkmark",
		size: 24
	});
}
function Jr(e) {
	switch (e) {
		case "collapse": return /* @__PURE__ */ m(Gr, {});
		case "commence": return /* @__PURE__ */ m(Kr, {});
		case "selected": return /* @__PURE__ */ m(qr, {});
	}
}
function Yr({ 标题: e = "标题", 菜单项: t = [], 组数: n = 3, 通透度: r = "弱", leftIcon: i, rightIcon: a, rightIconState: o = "collapse", submenuCount: s = 3, openIndex: c, defaultOpenIndex: l = null, onOpenIndexChange: u, 显示图标: f, 显示状态: p, className: g, ..._ }) {
	let v = t.slice(0, n), [y, b] = d(l), x = r === "标准", S = i ?? f ?? !1, C = a ?? p ?? !1, w = Qr(c ?? y, v.length), T = (e, t) => {
		let n = w === t ? null : t;
		e.onClick?.(), c === void 0 && b(n), u?.(n);
	};
	return /* @__PURE__ */ h("div", {
		className: X("hm-floating-menu", x && "hm-material-style-layer-floating-thick-effect-1", g),
		"data-通透度": r,
		..._,
		children: [x ? Br.map((e) => /* @__PURE__ */ m("span", { className: X("hm-material-style-layer", e) }, e)) : null, /* @__PURE__ */ h("div", {
			className: "hm-floating-menu__content",
			children: [/* @__PURE__ */ m("div", {
				className: "hm-floating-menu__title",
				children: /* @__PURE__ */ m("span", {
					className: "hm-floating-menu__title-text",
					children: e
				})
			}), v.map((e, t) => {
				let n = Xr(e, s), r = w === t, i = e.leftIcon ?? e.显示图标 ?? S, a = e.rightIcon ?? e.显示状态 ?? C, c = r && n.length > 0 ? "commence" : e.rightIconState ?? e.状态 ?? o;
				return /* @__PURE__ */ h("div", {
					className: "hm-floating-menu__group",
					children: [/* @__PURE__ */ h("button", {
						type: "button",
						className: "hm-floating-menu__item",
						"aria-expanded": n.length > 0 ? r : void 0,
						onClick: () => T(e, t),
						children: [
							i && /* @__PURE__ */ m("span", {
								className: "hm-floating-menu__item-icon",
								children: e.icon ?? /* @__PURE__ */ m(Z, {
									name: Wr,
									size: 24
								})
							}),
							/* @__PURE__ */ m("span", {
								className: "hm-floating-menu__item-text",
								children: e.label
							}),
							a && /* @__PURE__ */ m("span", {
								className: "hm-floating-menu__item-trailing",
								children: e.trailing ?? Jr(c)
							})
						]
					}), r && n.length > 0 ? /* @__PURE__ */ m("div", {
						className: "hm-floating-menu__submenu",
						children: n.map((e, t) => /* @__PURE__ */ m("button", {
							className: "hm-floating-menu__submenu-item",
							type: "button",
							onClick: e.onClick,
							children: /* @__PURE__ */ m("span", {
								className: "hm-floating-menu__submenu-text",
								children: e.label
							})
						}, `${e.label}-${t}`))
					}) : null]
				}, t);
			})]
		})]
	});
}
function Xr(e, t) {
	let n = e.submenuItems ?? e.子菜单项;
	return n ? n.slice(0, 6) : Zr(e.submenuCount ?? t);
}
function Zr(e) {
	return Array.from({ length: e }, () => ({ label: "menu item" }));
}
function Qr(e, t) {
	return e == null || t <= 0 ? null : Math.min(Math.max(e, 0), t - 1);
}
//#endregion
//#region src/components/Controls/FloatingMenu/index.ts
var $r = /* @__PURE__ */ _({
	FloatingMenu: () => Yr,
	floatingMenuGroupCounts: () => Vr,
	floatingMenuItemStates: () => Ur,
	floatingMenuOpacities: () => Hr
}), ei = [
	"Text with icon",
	"Text with subtitle",
	"subMenu",
	"PopupMenu"
], ti = [
	"Normal",
	"selected",
	"right element",
	"with select",
	"List title"
], ni = [
	"collapse",
	"commence",
	"selected"
], ri = [
	"1",
	"2",
	"3",
	"4",
	"5",
	"6"
], ii = [
	"标准",
	"高",
	"降档",
	"弱"
], ai = [
	"上1",
	"上2",
	"上3",
	"下1",
	"下2",
	"下3",
	"左1",
	"左2",
	"左3",
	"右1",
	"右2",
	"右3"
];
function oi() {
	return /* @__PURE__ */ m(Z, {
		name: "segmented_button_highlight",
		size: 24
	});
}
function si() {
	return /* @__PURE__ */ m(Z, {
		name: "chevron_right",
		size: 24
	});
}
function ci() {
	return /* @__PURE__ */ m(Z, {
		name: "chevron_down",
		size: 24
	});
}
function li() {
	return /* @__PURE__ */ m(Z, {
		name: "checkmark",
		size: 24
	});
}
var ui = [{
	标题: "Title",
	菜单项: [
		{
			label: "Menu Item",
			icon: /* @__PURE__ */ m(oi, {}),
			状态: "collapse"
		},
		{
			label: "Menu Item",
			icon: /* @__PURE__ */ m(oi, {}),
			状态: "collapse"
		},
		{
			label: "Menu Item",
			icon: /* @__PURE__ */ m(oi, {}),
			状态: "collapse"
		}
	]
}], di = [{ 菜单项: [
	{
		label: "菜单选项",
		icon: /* @__PURE__ */ m(oi, {}),
		类型: "Normal"
	},
	{
		label: "菜单选项",
		icon: /* @__PURE__ */ m(oi, {}),
		类型: "Normal"
	},
	{
		label: "菜单选项",
		icon: /* @__PURE__ */ m(oi, {}),
		类型: "Normal"
	},
	{
		label: "菜单选项",
		icon: /* @__PURE__ */ m(oi, {}),
		类型: "Normal"
	}
] }];
function fi({ item: e }) {
	let t = e.trailing ?? (e.状态 === "collapse" ? /* @__PURE__ */ m(si, {}) : e.状态 === "commence" ? /* @__PURE__ */ m(ci, {}) : e.状态 === "selected" ? /* @__PURE__ */ m(li, {}) : null);
	return /* @__PURE__ */ h("button", {
		type: "button",
		className: X("hm-menu__phone-item", e.状态 === "selected" && "hm-menu__phone-item--selected", e.disabled && "hm-menu__phone-item--disabled"),
		onClick: e.onClick,
		disabled: e.disabled,
		children: [
			e.icon && /* @__PURE__ */ m("span", {
				className: "hm-menu__phone-item-icon",
				children: e.icon
			}),
			/* @__PURE__ */ h("span", {
				className: "hm-menu__phone-item-text-frame",
				children: [/* @__PURE__ */ m("span", {
					className: "hm-menu__phone-item-label",
					children: e.label
				}), /* @__PURE__ */ m($, {
					尺寸: "0.5",
					颜色: "rgba(0, 0, 0, 0.2)",
					className: "hm-menu__phone-item-divider",
					"aria-hidden": "true"
				})]
			}),
			t && /* @__PURE__ */ m("span", {
				className: "hm-menu__phone-item-trailing",
				children: t
			})
		]
	});
}
function pi({ item: e, 菜单类型: t }) {
	let n = e.类型 ?? "Normal", r = n === "List title", i = t === "Text with subtitle" && e.subtitle, a = e.trailing ?? (n === "Normal" ? /* @__PURE__ */ m(si, {}) : n === "selected" || n === "with select" ? /* @__PURE__ */ m(li, {}) : null), o = n === "Normal" || n === "selected" || n === "with select";
	return /* @__PURE__ */ h("button", {
		type: "button",
		className: X("hm-menu__pc-item", `hm-menu__pc-item--${n.replace(/\s+/g, "-")}`, e.disabled && "hm-menu__pc-item--disabled"),
		onClick: e.onClick,
		disabled: r || e.disabled,
		children: [
			/* @__PURE__ */ m("span", {
				className: "hm-menu__pc-item-bg",
				"aria-hidden": !0
			}),
			e.icon && !r && /* @__PURE__ */ m("span", {
				className: "hm-menu__pc-item-icon",
				children: e.icon
			}),
			/* @__PURE__ */ m("span", {
				className: "hm-menu__pc-item-label",
				children: e.label
			}),
			i && /* @__PURE__ */ m("span", {
				className: "hm-menu__pc-item-subtitle",
				children: e.subtitle
			}),
			e.shortcut && /* @__PURE__ */ m("span", {
				className: "hm-menu__pc-item-shortcut",
				children: e.shortcut
			}),
			o && /* @__PURE__ */ m("span", {
				className: "hm-menu__pc-item-trailing",
				children: a
			})
		]
	});
}
function mi({ 标题: e }) {
	return /* @__PURE__ */ m("div", {
		className: "hm-menu__title",
		children: /* @__PURE__ */ m("span", {
			className: "hm-menu__title-text",
			children: e
		})
	});
}
function hi({ 外观: e = "手机", 菜单类型: t = "Text with icon", items: n, 浮动: r = !1, 通透度: i = "标准", className: a, ...o }) {
	let s = n && n.length > 0 ? n : e === "手机" ? ui : di, c = e === "手机";
	return /* @__PURE__ */ m("div", {
		className: X("hm-menu", c ? "hm-menu--phone" : `hm-menu--pc hm-menu--pc-${t.replace(/\s+/g, "-")}`, r && "hm-menu--floating", r && `hm-menu--transparency-${i}`, a),
		"data-外观": e,
		"data-菜单类型": t,
		"data-浮动": r ? "true" : void 0,
		...o,
		children: /* @__PURE__ */ m("div", {
			className: "hm-menu__inner",
			children: s.map((e, n) => /* @__PURE__ */ h("div", {
				className: "hm-menu__group",
				children: [
					e.标题 && /* @__PURE__ */ m(mi, { 标题: e.标题 }),
					/* @__PURE__ */ m("div", {
						className: "hm-menu__items",
						children: e.菜单项.map((e, n) => /* @__PURE__ */ m("div", {
							className: "hm-menu__item-wrapper",
							children: c ? /* @__PURE__ */ m(fi, { item: e }) : /* @__PURE__ */ m(pi, {
								item: e,
								菜单类型: t
							})
						}, n))
					}),
					n < s.length - 1 && /* @__PURE__ */ m($, {
						尺寸: "0.5",
						颜色: "rgba(0, 0, 0, 0.2)",
						className: "hm-menu__divider",
						"aria-hidden": "true"
					})
				]
			}, n))
		})
	});
}
//#endregion
//#region src/components/Controls/Menu/index.ts
var gi = /* @__PURE__ */ _({
	Menu: () => hi,
	menuGroupCounts: () => ri,
	menuItemStates: () => ni,
	menuItemTypes: () => ti,
	menuPositions: () => ai,
	menuTransparencies: () => ii,
	menuTypes: () => ei
});
//#endregion
//#region src/components/Controls/Select/select-shared.ts
function _i({ options: e, value: t, defaultValue: n, onValueChange: r, placeholder: i = "Select", disabled: a = !1 }) {
	let [o, l] = d(!1), [f, p] = d(n ?? ""), m = u(null), h = c(), g = !!e?.length && !a, _ = t ?? f, v = e?.find((e) => e.value === _)?.label ?? i;
	return s(() => {
		if (!o) return;
		let e = (e) => {
			m.current?.contains(e.target) || l(!1);
		};
		return document.addEventListener("mousedown", e), () => document.removeEventListener("mousedown", e);
	}, [o]), {
		interactive: g,
		label: v,
		menuId: h,
		menuItems: g ? [{ 菜单项: e.map((e) => ({
			label: e.label,
			类型: _ === e.value ? "with select" : "Normal",
			disabled: e.disabled,
			onClick: () => {
				e.disabled || (t === void 0 && p(e.value), r?.(e.value), l(!1));
			}
		})) }] : [],
		open: o,
		rootRef: m,
		toggle: () => {
			g && l((e) => !e);
		}
	};
}
//#endregion
//#region src/components/Controls/FloatingSelectPhone/FloatingSelectPhone.tsx
var vi = [
	"hm-material-style-layer-floating-ultra-thin-fill-1",
	"hm-material-style-layer-floating-ultra-thin-fill-2",
	"hm-material-style-layer-floating-ultra-thin-effect-1",
	"hm-material-style-layer-floating-ultra-thin-effect-3",
	"hm-material-style-layer-floating-ultra-thin-effect-4",
	"hm-material-style-layer-floating-ultra-thin-effect-5",
	"hm-material-style-layer-floating-ultra-thin-effect-6",
	"hm-material-style-layer-floating-ultra-thin-effect-7",
	"hm-material-style-layer-floating-ultra-thin-effect-8"
];
function yi({ 尺寸: e = "Medium", 状态: t = "Enabled", 通透度: n = "弱", 文本: r = "Select", options: i, value: a, defaultValue: o, onValueChange: s, placeholder: c, className: l, onClick: u, ...d }) {
	let f = t === "Disabled", { interactive: p, label: g, menuId: _, menuItems: v, open: y, rootRef: b, toggle: x } = _i({
		options: i,
		value: a,
		defaultValue: o,
		onValueChange: s,
		placeholder: c ?? r,
		disabled: f
	}), S = Si({
		interactive: p,
		open: y,
		state: t
	}), C = p ? g : r, w = bi(C, e), T = n === "标准";
	return /* @__PURE__ */ h("div", {
		ref: b,
		className: "hm-floating-select-phone-root",
		children: [/* @__PURE__ */ h("button", {
			type: "button",
			className: X("hm-floating-select-phone", `hm-floating-select-phone--size-${e.toLowerCase()}`, `hm-floating-select-phone--state-${S.toLowerCase()}`, `hm-floating-select-phone--opacity-${xi(n)}`, T && "hm-material-style-layer-floating-ultra-thin-effect-2", l),
			"aria-disabled": f || void 0,
			"aria-expanded": p ? y : void 0,
			"aria-haspopup": p ? "listbox" : void 0,
			"aria-controls": p && y ? _ : void 0,
			"data-size": e,
			"data-state": S,
			"data-opacity": n,
			disabled: f,
			onClick: (e) => {
				p && x(), u?.(e);
			},
			...d,
			children: [T ? vi.map((e) => /* @__PURE__ */ m("span", { className: X("hm-material-style-layer", e) }, e)) : null, /* @__PURE__ */ h("span", {
				className: "hm-floating-select-phone__content",
				children: [/* @__PURE__ */ m("span", {
					className: "hm-floating-select-phone__label",
					"aria-label": C,
					children: w
				}), /* @__PURE__ */ m(Ci, {})]
			})]
		}), y && p ? /* @__PURE__ */ m("div", {
			className: "hm-floating-select-phone-root__menu",
			id: _,
			children: /* @__PURE__ */ m(hi, {
				外观: "PC",
				菜单类型: "PopupMenu",
				items: v
			})
		}) : null]
	});
}
function bi(e, t) {
	return t !== "Small" || e.length <= 2 ? e : `${e.slice(0, 2)}...`;
}
function xi(e) {
	return {
		弱: "weak",
		降档: "downgraded",
		高: "high",
		标准: "standard"
	}[e];
}
function Si({ interactive: e, open: t, state: n }) {
	return n === "Disabled" || !e ? n : t ? "Pressed" : n;
}
function Ci({ className: e }) {
	return /* @__PURE__ */ m(Z, {
		className: X("hm-floating-select-phone__arrow", e),
		name: "arrowtriangle_down_fill",
		size: 24
	});
}
//#endregion
//#region src/components/Controls/FloatingSelectPhone/floating-select-phone.constants.ts
var wi = ["Medium", "Small"], Ti = [
	"Enabled",
	"Hover",
	"Pressed",
	"Focus",
	"Disabled"
], Ei = [
	"弱",
	"降档",
	"高",
	"标准"
], Di = /* @__PURE__ */ _({
	FloatingSelectPhone: () => yi,
	floatingSelectPhoneOpacities: () => Ei,
	floatingSelectPhoneSizes: () => wi,
	floatingSelectPhoneStates: () => Ti
}), Oi = ["中文", "英文"], ki = ["标准"], Ai = {
	中文: [
		"剪切",
		"复制",
		"全选",
		"翻译",
		"分享"
	],
	英文: [
		"CUT",
		"COPY",
		"SELECT ALL"
	]
}, ji = [
	"hm-material-style-layer-floating-thick-fill-1",
	"hm-material-style-layer-floating-thick-fill-2",
	"hm-material-style-layer-floating-thick-effect-2",
	"hm-material-style-layer-floating-thick-effect-3",
	"hm-material-style-layer-floating-thick-effect-4",
	"hm-material-style-layer-floating-thick-effect-5",
	"hm-material-style-layer-floating-thick-effect-6",
	"hm-material-style-layer-floating-thick-effect-7",
	"hm-material-style-layer-floating-thick-effect-8"
];
function Mi({ 语言: e = "中文", 通透度: t = "标准", labels: n, onAction: r, className: i, ...a }) {
	let o = n ?? Ai[e], s = t === "标准";
	return /* @__PURE__ */ h("div", {
		className: X("hm-floating-text-selection", s && "hm-material-style-layer-floating-thick-effect-1", Q("FloatingTextSelection", {
			语言: e,
			通透度: t
		}), i),
		"data-language": e,
		"data-opacity": t,
		role: "toolbar",
		"aria-label": "Text selection actions",
		...a,
		children: [s ? ji.map((e) => /* @__PURE__ */ m("span", {
			"aria-hidden": "true",
			className: X("hm-material-style-layer", e)
		}, e)) : null, /* @__PURE__ */ h("div", {
			className: "hm-floating-text-selection__content",
			children: [/* @__PURE__ */ m("div", {
				className: "hm-floating-text-selection__actions",
				children: o.map((t, n) => /* @__PURE__ */ m("button", {
					className: "hm-floating-text-selection__action",
					onClick: () => r?.(t, n),
					type: "button",
					children: t
				}, `${e}-${t}-${n}`))
			}), /* @__PURE__ */ m("button", {
				className: "hm-floating-text-selection__more",
				type: "button",
				"aria-label": e === "中文" ? "更多" : "More",
				children: /* @__PURE__ */ m(Z, {
					name: "dot_grid_2x2",
					size: 19.2,
					"aria-hidden": !0
				})
			})]
		})]
	});
}
//#endregion
//#region src/components/Controls/FloatingTextSelection/index.ts
var Ni = /* @__PURE__ */ _({
	FloatingTextSelection: () => Mi,
	floatingTextSelectionLabels: () => Ai,
	floatingTextSelection语言Options: () => Oi,
	floatingTextSelection通透度Options: () => ki
}), Pi = [
	"hm-material-style-layer-floating-thin-fill-1",
	"hm-material-style-layer-floating-thin-fill-2",
	"hm-material-style-layer-floating-thin-effect-1",
	"hm-material-style-layer-floating-thin-effect-3",
	"hm-material-style-layer-floating-thin-effect-4",
	"hm-material-style-layer-floating-thin-effect-5",
	"hm-material-style-layer-floating-thin-effect-6",
	"hm-material-style-layer-floating-thin-effect-7",
	"hm-material-style-layer-floating-thin-effect-8"
], Fi = [
	"3",
	"4",
	"5",
	"6",
	"纵向-icon"
], Ii = [
	"标准",
	"强",
	"降档",
	"弱"
], Li = ["Enable", "Activated"], Ri = 1;
function zi(e, t) {
	return t <= 0 ? -1 : Number.isFinite(e) ? Math.max(0, Math.min(Math.trunc(e), t - 1)) : 0;
}
var Bi = {
	3: 3,
	4: 4,
	5: 5,
	6: 6,
	"纵向-icon": 4
};
function Vi() {
	return /* @__PURE__ */ m(Z, {
		name: "heart",
		size: 24,
		style: { fontVariationSettings: "\"FILL\" 0, \"wght\" 400, \"GRAD\" 0, \"opsz\" 24" }
	});
}
function Hi() {
	return /* @__PURE__ */ m(Z, {
		name: "heart_fill",
		size: 24
	});
}
function Ui(e, t) {
	let n = Bi[e];
	return t?.length ? t.slice(0, n).map((e, t) => ({
		ariaLabel: e.ariaLabel ?? `Tool action ${t + 1}`,
		icon: e.icon ?? /* @__PURE__ */ m(Vi, {}),
		activatedIcon: e.activatedIcon ?? /* @__PURE__ */ m(Hi, {}),
		onClick: e.onClick,
		状态: e.状态
	})) : Array.from({ length: n }, (e, t) => ({
		ariaLabel: `Tool action ${t + 1}`,
		icon: /* @__PURE__ */ m(Vi, {}),
		activatedIcon: /* @__PURE__ */ m(Hi, {})
	}));
}
function Wi({ "属性 1": e = "3", 通透度: t = "标准", items: n, selectedIndex: r, defaultSelectedIndex: i = Ri, onSelectedIndexChange: a, onActiveChange: o, className: s, ...c }) {
	let l = Ui(e, n), [u, f] = d(() => zi(i, l.length)), p = zi(r ?? u, l.length), g = l.map((e, t) => ({
		...e,
		状态: e.状态 ?? (t === p ? "Activated" : "Enable")
	})), _ = e === "纵向-icon", v = t === "标准";
	return /* @__PURE__ */ m("div", {
		className: X("hm-floating-toolbar-onlyicon-phone", s),
		"data-selected-index": p,
		"data-transparency": t,
		"data-variant": e,
		...c,
		children: /* @__PURE__ */ h("div", {
			className: X("hm-floating-toolbar-onlyicon-phone__surface", _ && "hm-floating-toolbar-onlyicon-phone__surface--vertical", v && "hm-material-style-layer-floating-thin-effect-2"),
			children: [v ? Pi.map((e) => /* @__PURE__ */ m("span", { className: X("hm-material-style-layer", e) }, e)) : null, g.map((t, n) => /* @__PURE__ */ h("div", {
				className: "hm-floating-toolbar-onlyicon-phone__slot",
				"data-index": n,
				children: [/* @__PURE__ */ m("button", {
					"aria-label": t.ariaLabel,
					className: X("hm-floating-toolbar-onlyicon-phone__button", t.状态 === "Activated" && "hm-floating-toolbar-onlyicon-phone__button--activated"),
					onClick: (e) => {
						r === void 0 && f(n), a?.(n), o?.(n), t.onClick?.(e);
					},
					type: "button",
					children: /* @__PURE__ */ m("span", {
						className: "hm-floating-toolbar-onlyicon-phone__icon",
						children: t.状态 === "Activated" ? t.activatedIcon : t.icon
					})
				}), e === "6" && n === 0 ? /* @__PURE__ */ m($, {
					方向: "vertical",
					尺寸: "1",
					颜色: "rgba(0, 0, 0, 0.12)",
					"aria-hidden": "true",
					className: "hm-floating-toolbar-onlyicon-phone__divider"
				}) : null]
			}, `${e}-${n}`))]
		})
	});
}
//#endregion
//#region src/components/Controls/FloatingToolBarOnlyiconPhone/index.ts
var Gi = /* @__PURE__ */ _({
	FloatingToolBarOnlyiconPhone: () => Wi,
	floatingToolBarOnlyiconPhoneStates: () => Li,
	floatingToolBarOnlyiconPhoneTransparencies: () => Ii,
	floatingToolBarOnlyiconPhoneVariants: () => Fi
}), Ki = [
	"hm-material-style-layer-floating-thin-fill-1",
	"hm-material-style-layer-floating-thin-fill-2",
	"hm-material-style-layer-floating-thin-effect-1",
	"hm-material-style-layer-floating-thin-effect-3",
	"hm-material-style-layer-floating-thin-effect-4",
	"hm-material-style-layer-floating-thin-effect-5",
	"hm-material-style-layer-floating-thin-effect-6",
	"hm-material-style-layer-floating-thin-effect-7",
	"hm-material-style-layer-floating-thin-effect-8"
], qi = [
	"3",
	"4",
	"5",
	"6",
	"纵向-icon"
], Ji = [
	"标准",
	"平滑",
	"降档",
	"弱"
], Yi = ["Enable", "Activated"], Xi = 1;
function Zi(e, t) {
	return t <= 0 ? -1 : Number.isFinite(e) ? Math.max(0, Math.min(Math.trunc(e), t - 1)) : 0;
}
var Qi = {
	3: 3,
	4: 4,
	5: 5,
	6: 6,
	"纵向-icon": 4
};
function $i() {
	return /* @__PURE__ */ m(Z, {
		name: "heart",
		size: 24,
		style: { fontVariationSettings: "\"FILL\" 0, \"wght\" 400, \"GRAD\" 0, \"opsz\" 24" }
	});
}
function ea() {
	return /* @__PURE__ */ m(Z, {
		name: "heart_fill",
		size: 24
	});
}
function ta(e, t) {
	let n = Qi[e];
	return t?.length ? t.slice(0, n).map((e, t) => ({
		ariaLabel: e.ariaLabel ?? e.label ?? `Tab ${t + 1}`,
		label: e.label ?? "Tab",
		icon: e.icon ?? /* @__PURE__ */ m($i, {}),
		activatedIcon: e.activatedIcon ?? /* @__PURE__ */ m(ea, {}),
		onClick: e.onClick,
		状态: e.状态
	})) : Array.from({ length: n }, (e, t) => ({
		ariaLabel: `Tab ${t + 1}`,
		label: "Tab",
		icon: /* @__PURE__ */ m($i, {}),
		activatedIcon: /* @__PURE__ */ m(ea, {})
	}));
}
function na({ "属性 1": e = "3", 通透度: t = "标准", items: n, selectedIndex: r, defaultSelectedIndex: i = Xi, onSelectedIndexChange: a, onActiveChange: o, className: s, ...c }) {
	let l = ta(e, n), [u, f] = d(() => Zi(i, l.length)), p = Zi(r ?? u, l.length), g = l.map((e, t) => ({
		...e,
		状态: e.状态 ?? (t === p ? "Activated" : "Enable")
	})), _ = e === "纵向-icon", v = t === "标准";
	return /* @__PURE__ */ m("div", {
		className: X("hm-floating-toolbar-text-phone", s),
		"data-selected-index": p,
		"data-transparency": t,
		"data-variant": e,
		...c,
		children: /* @__PURE__ */ h("div", {
			className: X("hm-floating-toolbar-text-phone__surface", _ && "hm-floating-toolbar-text-phone__surface--vertical", v && "hm-material-style-layer-floating-thin-effect-2"),
			children: [v ? Ki.map((e) => /* @__PURE__ */ m("span", { className: X("hm-material-style-layer", e) }, e)) : null, g.map((t, n) => /* @__PURE__ */ m("div", {
				className: "hm-floating-toolbar-text-phone__slot",
				"data-index": n,
				children: /* @__PURE__ */ h("button", {
					"aria-label": t.ariaLabel,
					className: X("hm-floating-toolbar-text-phone__button", t.状态 === "Activated" && "hm-floating-toolbar-text-phone__button--activated"),
					onClick: (e) => {
						r === void 0 && f(n), a?.(n), o?.(n), t.onClick?.(e);
					},
					type: "button",
					children: [/* @__PURE__ */ m("span", {
						className: "hm-floating-toolbar-text-phone__icon",
						children: t.状态 === "Activated" ? t.activatedIcon : t.icon
					}), /* @__PURE__ */ m("span", {
						className: "hm-floating-toolbar-text-phone__label",
						children: t.label
					})]
				})
			}, `${e}-${n}`))]
		})
	});
}
//#endregion
//#region src/components/Controls/FloatingToolBarTextPhone/index.ts
var ra = /* @__PURE__ */ _({
	FloatingToolBarTextPhone: () => na,
	floatingToolBarTextPhoneStates: () => Yi,
	floatingToolBarTextPhoneTransparencies: () => Ji,
	floatingToolBarTextPhoneVariants: () => qi
}), ia = e.forwardRef(({ 状态: e = "normal", className: t, ...n }, r) => /* @__PURE__ */ m("div", {
	ref: r,
	role: "scrollbar",
	"aria-valuenow": void 0,
	className: X("flex h-20 w-8 items-center justify-end", t),
	...n,
	children: /* @__PURE__ */ m("div", { className: X("h-full rounded-full bg-[rgba(0,0,0,1)] opacity-40 transition-[width] duration-150 ease-out", e === "press" ? "w-2" : "w-1") })
}));
ia.displayName = "ScrollBarThumb";
var aa = e.forwardRef(({ orientation: e = "vertical", className: t, ...n }, r) => e === "horizontal" ? /* @__PURE__ */ m("div", {
	ref: r,
	className: X("flex h-8 w-20 items-center", t),
	...n,
	children: /* @__PURE__ */ m("div", { className: "h-1 w-full rounded-full bg-[rgba(0,0,0,1)] opacity-40 transition-[height] duration-150 ease-out" })
}) : /* @__PURE__ */ m("div", {
	ref: r,
	className: X("flex h-20 w-8", t),
	...n
}));
aa.displayName = "ScrollBar";
//#endregion
//#region src/components/Controls/ScrollBar/index.ts
var oa = /* @__PURE__ */ _({
	ScrollBar: () => aa,
	ScrollBarThumb: () => ia
}), sa = ["Medium", "Small"], ca = [
	"Enabled",
	"Hover",
	"Pressed",
	"Focused",
	"Disabled"
];
function la({ className: e }) {
	return /* @__PURE__ */ m(Z, {
		className: X("hm-select-phone__arrow", e),
		name: "arrowtriangle_down_fill",
		size: 24
	});
}
function ua({ interactive: e, open: t, state: n }) {
	return n === "Disabled" || !e ? n : t ? "Pressed" : n === "Focused" ? "Focused" : "Enabled";
}
function da({ 尺寸: e = "Medium", 状态: t = "Enabled", options: n, value: r, defaultValue: i, onValueChange: a, placeholder: o = "Select", className: s, onClick: c, ...l }) {
	let u = t === "Disabled", { interactive: d, label: f, menuId: p, menuItems: g, open: _, rootRef: v, toggle: y } = _i({
		options: n,
		value: r,
		defaultValue: i,
		onValueChange: a,
		placeholder: o,
		disabled: u
	}), b = ua({
		interactive: d,
		open: _,
		state: t
	}), x = fa(d ? f : "Select", e);
	return /* @__PURE__ */ h("div", {
		ref: v,
		className: "hm-select-root",
		children: [/* @__PURE__ */ h("button", {
			type: "button",
			className: X("hm-select-phone", `hm-select-phone--${e.toLowerCase()}`, `hm-select-phone--state-${b.toLowerCase()}`, s),
			"aria-disabled": u || void 0,
			"aria-expanded": d ? _ : void 0,
			"aria-haspopup": d ? "listbox" : void 0,
			"aria-controls": d && _ ? p : void 0,
			disabled: u,
			"data-size": e,
			"data-state": b,
			onClick: (e) => {
				d && y(), c?.(e);
			},
			...l,
			children: [/* @__PURE__ */ m("span", {
				className: "hm-select-phone__label",
				"aria-label": d ? f : "Select",
				children: x
			}), /* @__PURE__ */ m(la, {})]
		}), _ && d ? /* @__PURE__ */ m("div", {
			className: "hm-select-root__menu",
			id: p,
			children: /* @__PURE__ */ m(hi, {
				外观: "PC",
				菜单类型: "PopupMenu",
				items: g
			})
		}) : null]
	});
}
function fa(e, t) {
	return t !== "Small" || e.length <= 2 ? e : `${e.slice(0, 2)}...`;
}
//#endregion
//#region src/components/Controls/Select/select-2in1.tsx
var pa = ["normal", "small"], ma = [
	"Enabled",
	"Hover",
	"Pressed",
	"focused",
	"Disabled"
];
function ha() {
	return /* @__PURE__ */ m(Z, {
		className: "hm-select-2in1__arrow",
		name: "arrowtriangle_down_fill",
		size: 24
	});
}
function ga() {
	return /* @__PURE__ */ m(Z, {
		className: "hm-select-2in1__arrow",
		name: "arrowtriangle_down_fill",
		size: 24
	});
}
function _a({ interactive: e, open: t, state: n }) {
	return n === "Disabled" || !e ? n : t ? "Pressed" : n === "focused" ? "focused" : "Enabled";
}
function va({ 尺寸: e = "normal", 状态: t = "Enabled", options: n, value: r, defaultValue: i, onValueChange: a, placeholder: o = "Select", className: s, children: c, onClick: l, ...u }) {
	let d = t === "Disabled", { interactive: f, label: p, menuId: g, menuItems: _, open: v, rootRef: y, toggle: b } = _i({
		options: n,
		value: r,
		defaultValue: i,
		onValueChange: a,
		placeholder: o,
		disabled: d
	}), x = _a({
		interactive: f,
		open: v,
		state: t
	}), S = f ? p : c ?? o;
	return /* @__PURE__ */ h("div", {
		ref: y,
		className: "hm-select-root",
		children: [/* @__PURE__ */ h("button", {
			type: "button",
			className: X("hm-select-2in1", `hm-select-2in1--${e}`, `hm-select-2in1--state-${x.toLowerCase()}`, s),
			"aria-disabled": d || void 0,
			"aria-expanded": f ? v : void 0,
			"aria-haspopup": f ? "listbox" : void 0,
			"aria-controls": f && v ? g : void 0,
			disabled: d,
			"data-size": e,
			"data-state": x,
			onClick: (e) => {
				f && b(), l?.(e);
			},
			...u,
			children: [/* @__PURE__ */ m("span", {
				className: "hm-select-2in1__label",
				children: S
			}), m(e === "normal" ? ha : ga, {})]
		}), v && f ? /* @__PURE__ */ m("div", {
			className: "hm-select-root__menu",
			id: g,
			children: /* @__PURE__ */ m(hi, {
				外观: "PC",
				菜单类型: "PopupMenu",
				items: _
			})
		}) : null]
	});
}
//#endregion
//#region src/components/Controls/Select/index.ts
var ya = /* @__PURE__ */ _({
	Select: () => da,
	Select2in1: () => va,
	select2in1Sizes: () => pa,
	select2in1States: () => ma,
	selectSizes: () => sa,
	selectStates: () => ca
}), ba = ["中文", "英文"], xa = [
	40,
	32,
	28
], Sa = [
	{ label: "全选" },
	{ label: "复制" },
	{ label: "剪切" },
	{ label: "粘贴" },
	{ label: "选择" }
], Ca = [
	{ label: "Select All" },
	{ label: "Copy" },
	{ label: "Cut" },
	{ label: "Paste" }
];
function wa(e) {
	return e === "中文" ? Sa : Ca;
}
//#endregion
//#region src/components/Controls/TextSelection/TextSelection.tsx
function Ta({ 语言: e = "中文", className: t, ...n }) {
	let r = wa(e);
	return /* @__PURE__ */ h("div", {
		className: X("hm-text-selection", Q("TextSelection", { 语言: e }), t),
		"data-language": e,
		role: "toolbar",
		"aria-label": e === "中文" ? "文本选择工具栏" : "Text selection toolbar",
		...n,
		children: [r.map((t, n) => /* @__PURE__ */ m("button", {
			className: "hm-text-selection__item",
			type: "button",
			children: t.label
		}, `${e}-${t.label}-${n}`)), /* @__PURE__ */ m("button", {
			className: "hm-text-selection__more",
			type: "button",
			"aria-label": e === "中文" ? "更多" : "More",
			children: /* @__PURE__ */ m(Z, {
				className: "hm-text-selection__more-glyph",
				name: "dot_grid_2x2",
				size: 24
			})
		})]
	});
}
//#endregion
//#region src/components/Controls/TextSelection/index.ts
var Ea = /* @__PURE__ */ _({
	TextSelection: () => Ta,
	textSelection尺寸Options: () => xa,
	textSelection语言Options: () => ba
}), Da = ["Hander bottom", "Hander top"], Oa = "M9.75 0C9.33579 0 9 0.335786 9 0.75L9 21.0129C3.98572 21.2729 0 25.421 0 30.5C0 35.7467 4.25329 40 9.5 40C14.7467 40 19 35.7467 19 30.5C19 25.591 15.2767 21.5517 10.5 21.052L10.5 0.75C10.5 0.335786 10.1642 0 9.75 0ZM2 30.5C2 26.3579 5.35786 23 9.5 23C13.6421 23 17 26.3579 17 30.5C17 34.6421 13.6421 38 9.5 38C5.35786 38 2 34.6421 2 30.5Z", ka = "M0 9.5C0 4.25329 4.25329 0 9.5 0C14.7467 0 19 4.25329 19 9.5C19 14.409 15.2767 18.4483 10.5 18.948L10.5 39.25C10.5 39.6642 10.1642 40 9.75 40C9.33579 40 9 39.6642 9 39.25L9 18.9871C3.98572 18.7271 0 14.579 0 9.5ZM2 9.5C2 5.35786 5.35786 2 9.5 2C13.6421 2 17 5.35786 17 9.5C17 13.6421 13.6421 17 9.5 17C5.35786 17 2 13.6421 2 9.5Z";
function Aa({ 属性: e, className: t, ...n }) {
	let r = !e || e === "Hander bottom", i = !e || e === "Hander top";
	return /* @__PURE__ */ h("div", {
		className: X("hm-text-selection-handle", e !== void 0 && "hm-text-selection-handle--standalone", Q("TextSelectionHandle", { 属性: e }), t),
		role: "presentation",
		"aria-label": e === "Hander bottom" ? "文本选择底部手柄" : e === "Hander top" ? "文本选择顶部手柄" : "文本选择手柄",
		...n,
		children: [r && /* @__PURE__ */ m("svg", {
			className: "hm-text-selection-handle__icon hm-text-selection-handle__icon--bottom",
			viewBox: "0 0 19 40",
			width: "19",
			height: "40",
			fill: "none",
			"aria-hidden": "true",
			children: /* @__PURE__ */ m("path", {
				d: Oa,
				fill: "currentColor",
				fillRule: "evenodd"
			})
		}), i && /* @__PURE__ */ m("svg", {
			className: "hm-text-selection-handle__icon hm-text-selection-handle__icon--top",
			viewBox: "0 0 19 40",
			width: "19",
			height: "40",
			fill: "none",
			"aria-hidden": "true",
			children: /* @__PURE__ */ m("path", {
				d: ka,
				fill: "currentColor",
				fillRule: "evenodd"
			})
		})]
	});
}
//#endregion
//#region src/components/Controls/TextSelectionHandle/index.ts
var ja = /* @__PURE__ */ _({
	TextSelectionHandle: () => Aa,
	textSelectionHandle属性Options: () => Da
}), Ma = [
	"Enabled",
	"Hover",
	"Pressed",
	"Focus",
	"Disabled"
], Na = ["Selected", "Unselected"];
function Pa({ 状态: e = "Enabled", 类型: t = "Unselected", className: n, children: r, disabled: i, ...a }) {
	let o = {
		Enabled: "hm-toggle--enabled",
		Hover: "hm-toggle--hover",
		Pressed: "hm-toggle--pressed",
		Focus: "hm-toggle--focus",
		Disabled: "hm-toggle--disabled"
	}[e], s = {
		Selected: "hm-toggle--selected",
		Unselected: "hm-toggle--unselected"
	}[t];
	return /* @__PURE__ */ m("button", {
		className: X("hm-toggle", o, s, n),
		disabled: i ?? e === "Disabled",
		...a,
		children: r ?? "状态按钮"
	});
}
//#endregion
//#region src/components/Controls/Toggle/index.ts
var Fa = /* @__PURE__ */ _({
	Toggle: () => Pa,
	toggleStates: () => Ma,
	toggleTypes: () => Na
}), Ia = ["OFF", "ON"], La = [
	"2",
	"3",
	"4",
	"5"
], Ra = ["Enable", "Activated"], za = "Action", Ba = {
	"OFF-2": 1,
	"OFF-3": 2,
	"OFF-4": 1,
	"OFF-5": 1,
	"ON-2": 1,
	"ON-3": 2,
	"ON-4": 3,
	"ON-5": 4
};
function Va(e, t) {
	return t <= 0 ? -1 : Number.isFinite(e) ? Math.max(0, Math.min(Math.trunc(e), t - 1)) : 0;
}
function Ha() {
	return /* @__PURE__ */ m(Z, {
		name: "star",
		size: 24,
		style: { fontVariationSettings: "\"FILL\" 0, \"wght\" 400, \"GRAD\" 0, \"opsz\" 24" }
	});
}
function Ua() {
	return /* @__PURE__ */ m(Z, {
		name: "star_fill",
		size: 24
	});
}
function Wa(e, t) {
	let n = Number.parseInt(e, 10);
	return t?.length ? t.slice(0, n).map((e) => ({
		label: za,
		...e
	})) : Array.from({ length: n }, () => ({ label: za }));
}
function Ga({ Land: e = "OFF", 个数: t = "2", items: n, selectedIndex: r, defaultSelectedIndex: i, onSelectedIndexChange: o, onActiveChange: s, className: c, ...l }) {
	let u = Wa(t, n), f = Ba[`${e}-${t}`], [p, g] = d(() => Va(i ?? f, u.length)), _ = Va(r ?? p, u.length), v = u.map((e, t) => ({
		...e,
		状态: e.状态 ?? (t === _ ? "Activated" : "Enable")
	})), y = a((e, t) => {
		r === void 0 && g(e), o?.(e), s?.(e), t.onClick?.();
	}, [
		s,
		o,
		r
	]);
	return /* @__PURE__ */ h("div", {
		className: X("hm-toolbar-phone", `hm-toolbar-phone--land-${e}`, c),
		"data-selected-index": _,
		"data-count": t,
		"data-land": e,
		...l,
		children: [/* @__PURE__ */ m("div", {
			className: "hm-toolbar-phone__ports",
			children: v.map((e, t) => /* @__PURE__ */ h("button", {
				className: X("hm-toolbar-phone__port", e.状态 === "Activated" && "hm-toolbar-phone__port--activated"),
				onClick: () => y(t, e),
				type: "button",
				children: [/* @__PURE__ */ m("span", {
					className: "hm-toolbar-phone__icon",
					children: e.状态 === "Activated" ? e.activatedIcon ?? /* @__PURE__ */ m(Ua, {}) : e.icon ?? /* @__PURE__ */ m(Ha, {})
				}), /* @__PURE__ */ m("span", {
					className: "hm-toolbar-phone__label",
					children: e.label ?? za
				})]
			}, `${e.label ?? za}-${t}`))
		}), /* @__PURE__ */ m("div", {
			"aria-hidden": "true",
			className: "hm-toolbar-phone__bottom-bar",
			children: /* @__PURE__ */ m("span", { className: "hm-toolbar-phone__bottom-pill" })
		})]
	});
}
//#endregion
//#region src/components/Controls/ToolBar/index.ts
var Ka = /* @__PURE__ */ _({
	ToolBar: () => Ga,
	toolbarCounts: () => La,
	toolbarLands: () => Ia,
	toolbarPortStates: () => Ra
}), qa = [
	1,
	2,
	3
], Ja = [
	"材质-标准",
	"材质-强",
	"材质-降档"
], Ya = [
	40,
	32,
	28
], Xa = "square_dashed", Za = {
	"材质-标准": "hm-icon-button--material-standard",
	"材质-强": "hm-icon-button--material-strong",
	"材质-降档": "hm-icon-button--material-downgraded"
}, Qa = {
	40: "hm-icon-button--size-40",
	32: "hm-icon-button--size-32",
	28: "hm-icon-button--size-28"
}, $a = {
	40: 24,
	32: 20,
	28: 16
}, eo = [
	"hm-material-style-layer-floating-ultra-thin-fill-1",
	"hm-material-style-layer-floating-ultra-thin-fill-2",
	"hm-material-style-layer-floating-ultra-thin-effect-1",
	"hm-material-style-layer-floating-ultra-thin-effect-3",
	"hm-material-style-layer-floating-ultra-thin-effect-4",
	"hm-material-style-layer-floating-ultra-thin-effect-5",
	"hm-material-style-layer-floating-ultra-thin-effect-6",
	"hm-material-style-layer-floating-ultra-thin-effect-7",
	"hm-material-style-layer-floating-ultra-thin-effect-8"
];
function to({ Icon: e = 3, 通透度: t = "材质-标准", 尺寸: n = 40, glyphs: r, glyphNodes: i, glyphSize: a, className: o, ...s }) {
	let c = a ?? $a[n];
	return /* @__PURE__ */ m("div", {
		className: X("hm-icon-button", "hm-icon", Za[t], Qa[n], Q("IconButton", {
			Icon: String(e),
			通透度: t,
			尺寸: String(n),
			glyphs: r?.join(",") ?? ""
		}), o),
		"data-icon-count": e,
		"data-transparency": t,
		"data-size": n,
		role: "group",
		...s,
		children: Array.from({ length: e }, (e, n) => {
			let a = r?.[n] ?? Xa, o = i?.[n], s = t === "材质-标准";
			return /* @__PURE__ */ h("span", {
				"aria-hidden": "true",
				className: X("hm-icon-button__button hm-icon__button", s && "hm-material-style-layer-floating-ultra-thin-effect-2"),
				children: [s && eo.map((e) => /* @__PURE__ */ m("span", { className: X("hm-material-style-layer", e) }, e)), /* @__PURE__ */ m("span", {
					className: "hm-icon-button__content hm-icon__content",
					children: o ?? /* @__PURE__ */ m(Z, {
						className: "hm-icon-button__glyph hm-icon__glyph",
						name: a,
						size: c
					})
				})]
			}, `${t}-${a}-${n + 1}`);
		})
	});
}
//#endregion
//#region src/components/Publis/IconButton/index.ts
var no = /* @__PURE__ */ _({
	IconButton: () => to,
	iconButtonOptions: () => qa,
	iconButton尺寸Options: () => Ya,
	iconButton通透度Options: () => Ja
}), ro = /* @__PURE__ */ _({
	Icon: () => to,
	iconOptions: () => qa,
	icon通透度Options: () => Ja
}), io = [
	"default",
	"Text below",
	"Up and down"
], ao = ["notation", "arrows"];
function oo({ className: e }) {
	return /* @__PURE__ */ m(Z, {
		className: e,
		name: "plus",
		size: 24
	});
}
function so({ className: e }) {
	return /* @__PURE__ */ m(Z, {
		className: e,
		name: "minus",
		size: 24
	});
}
function co({ className: e }) {
	return /* @__PURE__ */ m(Z, {
		className: e,
		name: "chevron_up",
		size: 24,
		style: { height: 12 }
	});
}
function lo({ className: e }) {
	return /* @__PURE__ */ m(Z, {
		className: e,
		name: "chevron_down",
		size: 24,
		style: { height: 12 }
	});
}
function uo({ className: e }) {
	return /* @__PURE__ */ m(Z, {
		className: e,
		name: "chevron_left",
		size: 24
	});
}
function fo({ className: e }) {
	return /* @__PURE__ */ m(Z, {
		className: e,
		name: "chevron_right",
		size: 24
	});
}
function po({ size: e = 32, children: t, className: n, ...r }) {
	return /* @__PURE__ */ m("button", {
		type: "button",
		className: X("counter-icon-btn", e === 28 && "counter-icon-btn--sm", n),
		...r,
		children: t
	});
}
function mo({ 类型: e = "default", 步进器类型: t = "notation", value: n, defaultValue: r, label: i = "Quantity", min: o = 0, max: c = 999, step: l = 1, onChange: f, disabled: g = !1, className: _ }) {
	let v = n !== void 0, [y, b] = d(r ?? 999), x = v ? n : y, S = a((e) => {
		v || b(e), f?.(e);
	}, [v, f]), C = !g && x > o, w = !g && x < c, [T, E] = d(!1), [D, O] = d(""), k = u(null), A = u(!1);
	s(() => {
		if (T) {
			A.current = !0;
			let e = setTimeout(() => {
				k.current?.focus(), k.current?.select();
			}, 0);
			return () => clearTimeout(e);
		}
	}, [T]);
	let j = a(() => {
		g || T || (O(String(x)), E(!0));
	}, [
		g,
		T,
		x
	]), M = a(() => {
		E(!1), O("");
	}, []), N = a(() => {
		if (!T) return;
		E(!1);
		let e = Number(D);
		if (D === "" || isNaN(e)) {
			O("");
			return;
		}
		S(Math.max(o, Math.min(c, Math.round(e)))), O("");
	}, [
		T,
		D,
		o,
		c,
		S
	]), P = a((e) => {
		e.key === "Enter" ? (e.preventDefault(), N()) : e.key === "Escape" && (e.preventDefault(), M());
	}, [N, M]), F = a(() => {
		C && S(Math.max(o, x - l));
	}, [
		C,
		o,
		x,
		l,
		S
	]), I = a(() => {
		w && S(Math.min(c, x + l));
	}, [
		w,
		c,
		x,
		l,
		S
	]), L = (e) => /* @__PURE__ */ h("span", {
		className: X("counter-value-cell", e, T && "counter-value-cell--editing"),
		children: [/* @__PURE__ */ m("span", {
			className: "counter-value-text",
			onClick: () => j(),
			role: "button",
			tabIndex: g || T ? -1 : 0,
			children: String(x)
		}), /* @__PURE__ */ m("input", {
			ref: k,
			type: "text",
			inputMode: "numeric",
			className: "counter-value-input",
			value: D,
			onChange: (e) => O(e.target.value),
			onBlur: N,
			onKeyDown: P,
			autoComplete: "off"
		})]
	});
	return /* @__PURE__ */ h("div", {
		className: X("counter", `counter--type-${e}`, _),
		"data-type": e,
		"data-disabled": g || void 0,
		children: [
			e === "default" && /* @__PURE__ */ h("div", {
				className: "counter-default",
				children: [/* @__PURE__ */ h("div", {
					className: "counter-default__label-wrapper",
					children: [/* @__PURE__ */ m("span", {
						className: "counter-default__label",
						children: i
					}), /* @__PURE__ */ m($, {
						尺寸: "0.5",
						颜色: "var(--harmony-comp-divider, rgba(0, 0, 0, 0.2))",
						className: "counter-default__label-divider",
						"aria-hidden": "true"
					})]
				}), /* @__PURE__ */ m("div", {
					className: "counter-default__stepper",
					children: t === "arrows" ? /* @__PURE__ */ h(p, { children: [
						/* @__PURE__ */ m(po, {
							size: 32,
							onClick: F,
							disabled: !C,
							"aria-label": "Decrease",
							children: /* @__PURE__ */ m(uo, {})
						}),
						L("counter-default__value"),
						/* @__PURE__ */ m(po, {
							size: 32,
							onClick: I,
							disabled: !w,
							"aria-label": "Increase",
							children: /* @__PURE__ */ m(fo, {})
						})
					] }) : /* @__PURE__ */ h(p, { children: [
						/* @__PURE__ */ m(po, {
							size: 32,
							onClick: F,
							disabled: !C,
							"aria-label": "Decrease",
							children: /* @__PURE__ */ m(so, {})
						}),
						L("counter-default__value"),
						/* @__PURE__ */ m(po, {
							size: 32,
							onClick: I,
							disabled: !w,
							"aria-label": "Increase",
							children: /* @__PURE__ */ m(oo, {})
						})
					] })
				})]
			}),
			e === "Text below" && /* @__PURE__ */ h("div", {
				className: "counter-text-below",
				children: [/* @__PURE__ */ h("div", {
					className: "counter-text-below__pill",
					children: [
						/* @__PURE__ */ m(po, {
							size: 28,
							onClick: F,
							disabled: !C,
							"aria-label": "Decrease",
							children: /* @__PURE__ */ m(so, {})
						}),
						L("counter-text-below__value"),
						/* @__PURE__ */ m(po, {
							size: 28,
							onClick: I,
							disabled: !w,
							"aria-label": "Increase",
							children: /* @__PURE__ */ m(oo, {})
						})
					]
				}), /* @__PURE__ */ m("span", {
					className: "counter-text-below__label",
					children: i
				})]
			}),
			e === "Up and down" && /* @__PURE__ */ h("div", {
				className: "counter-up-down",
				children: [/* @__PURE__ */ m("span", {
					className: "counter-up-down__label",
					children: i
				}), /* @__PURE__ */ h("div", {
					className: "counter-up-down__box",
					children: [
						L("counter-up-down__value"),
						/* @__PURE__ */ m($, {
							方向: "vertical",
							尺寸: "1",
							颜色: "var(--harmony-comp-background-secondary, rgba(0, 0, 0, 0.098))",
							className: "counter-up-down__box-divider",
							"aria-hidden": "true"
						}),
						/* @__PURE__ */ h("div", {
							className: "counter-up-down__arrows",
							children: [
								/* @__PURE__ */ m("button", {
									type: "button",
									className: "counter-up-down__arrow-btn",
									onClick: I,
									disabled: !w,
									"aria-label": "Increase",
									children: /* @__PURE__ */ m(co, {})
								}),
								/* @__PURE__ */ m($, {
									尺寸: "1",
									颜色: "var(--harmony-comp-background-secondary, rgba(0, 0, 0, 0.098))",
									className: "counter-up-down__arrow-divider",
									"aria-hidden": "true"
								}),
								/* @__PURE__ */ m("button", {
									type: "button",
									className: "counter-up-down__arrow-btn",
									onClick: F,
									disabled: !C,
									"aria-label": "Decrease",
									children: /* @__PURE__ */ m(lo, {})
								})
							]
						})
					]
				})]
			})
		]
	});
}
//#endregion
//#region src/components/Input/Counter/index.ts
var ho = /* @__PURE__ */ _({
	Counter: () => mo,
	counterTypes: () => io,
	stepperTypes: () => ao
}), go = ["OFF", "ON"], _o = [
	"Normal",
	"Hover",
	"Press",
	"Focus",
	"Actived",
	"Typing",
	"Output",
	"icon hover",
	"icon focus",
	"icon press"
], vo = [
	"标准",
	"强",
	"降档",
	"弱"
], yo = [
	"hm-material-style-layer-floating-thin-fill-1",
	"hm-material-style-layer-floating-thin-fill-2",
	"hm-material-style-layer-floating-thin-effect-1",
	"hm-material-style-layer-floating-thin-effect-3",
	"hm-material-style-layer-floating-thin-effect-4",
	"hm-material-style-layer-floating-thin-effect-5",
	"hm-material-style-layer-floating-thin-effect-6",
	"hm-material-style-layer-floating-thin-effect-7",
	"hm-material-style-layer-floating-thin-effect-8"
];
function bo({ Search: e = "OFF", 状态: t, 通透度: n = "标准", placeholder: r = "搜索", searchButtonText: i = "Search", value: o, onChange: c, onSearch: l, className: f, disabled: p, onFocus: g, onBlur: _, ...v }) {
	let y = u(null), b = o !== void 0, [x, S] = d(""), C = b ? o : x, [w, T] = d("Normal"), E = t ?? w, D = E.toLowerCase().replace(/\s+/g, "-"), O = p === !0, k = C !== void 0 && C !== "", A = n === "标准";
	s(() => {
		!t || !y.current || (t === "Actived" ? (y.current.focus(), requestAnimationFrame(() => {
			y.current?.setSelectionRange(0, 0);
		})) : t === "Typing" && (y.current.focus(), requestAnimationFrame(() => {
			let e = String(C ?? "").length;
			y.current?.setSelectionRange(e, e);
		})));
	}, [t, C]);
	let j = a((e) => {
		g?.(e), t || T("Focus");
	}, [g, t]), M = a((e) => {
		_?.(e), t || T(k ? "Actived" : "Normal");
	}, [
		_,
		t,
		k
	]), N = a((e) => {
		b || S(e.target.value), c?.(e), t || T("Typing");
	}, [
		c,
		t,
		b
	]), P = a(() => {
		y.current?.focus();
	}, []), F = a((e) => {
		e.stopPropagation(), l?.(String(C ?? ""));
	}, [l, C]);
	return /* @__PURE__ */ h("div", {
		className: X("hm-floating-search-phone", A && "hm-material-style-layer-floating-thin-effect-2", f),
		"data-search": e,
		"data-state": D,
		"data-transparency": n,
		onClick: P,
		"aria-disabled": O || void 0,
		role: "searchbox",
		children: [
			A ? yo.map((e) => /* @__PURE__ */ m("span", { className: X("hm-material-style-layer", e) }, e)) : null,
			/* @__PURE__ */ m("span", { className: "hm-fsp__overlay" }),
			/* @__PURE__ */ m("span", {
				className: "hm-fsp__icon",
				"aria-hidden": "true",
				children: /* @__PURE__ */ m(Z, {
					name: "magnifyingglass",
					size: 16
				})
			}),
			/* @__PURE__ */ m("input", {
				ref: y,
				type: "text",
				className: "hm-fsp__input",
				placeholder: r,
				value: C,
				onChange: N,
				onFocus: j,
				onBlur: M,
				disabled: O,
				...v
			}),
			e === "OFF" && (E === "Typing" || E === "Output") && /* @__PURE__ */ m("span", {
				className: "hm-fsp__cancel",
				onClick: (e) => {
					e.stopPropagation(), b || S(""), c?.({ target: { value: "" } }), t || T("Normal");
				},
				role: "button",
				tabIndex: O ? -1 : 0,
				"aria-label": "Clear",
				children: /* @__PURE__ */ m(Z, {
					name: "xmark",
					size: 18
				})
			}),
			e === "ON" && /* @__PURE__ */ h("span", {
				className: "hm-fsp__action",
				children: [
					/* @__PURE__ */ m("span", {
						className: "hm-fsp__action-voice",
						onClick: (e) => e.stopPropagation(),
						role: "button",
						tabIndex: O ? -1 : 0,
						children: E === "Typing" || E === "Output" ? /* @__PURE__ */ m(Z, {
							name: "xmark",
							size: 18
						}) : /* @__PURE__ */ m(Z, {
							name: "mic",
							size: 18
						})
					}),
					/* @__PURE__ */ m($, {
						方向: "vertical",
						尺寸: "1",
						颜色: "var(--harmony-comp-divider, rgba(0, 0, 0, 0.2))",
						className: "hm-fsp__action-divider",
						"aria-hidden": "true"
					}),
					/* @__PURE__ */ m("span", {
						className: "hm-fsp__action-button",
						onClick: F,
						role: "button",
						tabIndex: O ? -1 : 0,
						children: i
					})
				]
			})
		]
	});
}
//#endregion
//#region src/components/Input/FloatingSearchPhone/index.ts
var xo = /* @__PURE__ */ _({
	FloatingSearchPhone: () => bo,
	floatingSearchPhoneOpacityOptions: () => vo,
	floatingSearchPhoneSearchOptions: () => go,
	floatingSearchPhoneStateOptions: () => _o
});
//#endregion
//#region src/components/Input/FloatingSearchSecondPagePhone/FloatingSearchSecondPagePhone.tsx
function So({ 通透度: e = "标准", 文本: t = "Music", 显示扫描: n = !0, 显示清除: r = !0, 显示光标: i = !0, 占位: a = !1, search: o = "OFF", 状态: s, onBackClick: c, onSearchClick: l, onScanClick: u, onClearClick: d, onSearch: f, className: p, ...g }) {
	let _ = (e) => (t) => {
		e && (t.key === "Enter" || t.key === " ") && (t.preventDefault(), e());
	}, v = (e) => {
		e.target.value === "" && d?.();
	};
	return /* @__PURE__ */ h("div", {
		className: X("hm-floating-search-second-page-phone", p),
		"data-opacity": e,
		"data-has-scan": n ? "true" : "false",
		"data-placeholder": a ? "true" : "false",
		...g,
		children: [
			/* @__PURE__ */ m(to, {
				Icon: 1,
				"aria-label": "返回",
				className: "hm-fssp__button hm-fssp__button--back",
				glyphNodes: [/* @__PURE__ */ m(wo, {}, "back")],
				onClick: c,
				onKeyDown: _(c),
				role: "button",
				tabIndex: c ? 0 : -1,
				通透度: Co(e),
				尺寸: 40
			}),
			/* @__PURE__ */ m(bo, {
				Search: o,
				className: X("hm-fssp__search", !r && "hm-fssp__search--hide-clear", !i && "hm-fssp__search--hide-caret"),
				defaultValue: a ? void 0 : t,
				onChange: v,
				onClick: l,
				onSearch: f,
				placeholder: a ? t : void 0,
				状态: s,
				通透度: e
			}),
			n ? /* @__PURE__ */ m(to, {
				Icon: 1,
				"aria-label": "扫描",
				className: "hm-fssp__button hm-fssp__button--scan",
				glyphNodes: [/* @__PURE__ */ m(To, {}, "scan")],
				onClick: u,
				onKeyDown: _(u),
				role: "button",
				tabIndex: u ? 0 : -1,
				通透度: Co(e),
				尺寸: 40
			}) : null
		]
	});
}
function Co(e) {
	switch (e) {
		case "标准": return "材质-标准";
		case "强": return "材质-强";
		case "降档": return "材质-降档";
		case "弱": return "材质-强";
	}
}
function wo() {
	return /* @__PURE__ */ m(Z, {
		name: "chevron_left",
		size: 24
	});
}
function To() {
	return /* @__PURE__ */ m(Z, {
		name: "line_viewfinder",
		size: 24
	});
}
//#endregion
//#region src/components/Input/FloatingSearchSecondPagePhone/floating-search-second-page-phone.constants.ts
var Eo = [
	"标准",
	"强",
	"降档",
	"弱"
], Do = /* @__PURE__ */ _({
	FloatingSearchSecondPagePhone: () => So,
	floatingSearchSecondPagePhoneOpacityOptions: () => Eo
}), Oo = [
	[9, 9],
	[105, 9],
	[201, 9],
	[9, 105],
	[105, 105],
	[201, 105],
	[9, 201],
	[105, 201],
	[201, 201]
], ko = 36, Ao = 18 / 2, jo = 7, Mo = 12, No = 210;
function Po(e, t, n) {
	let r = -1, i = ko;
	for (let a = 0; a < Oo.length; a++) {
		if (n.includes(a)) continue;
		let [o, s] = Oo[a], c = e - o, l = t - s, u = Math.sqrt(c * c + l * l);
		u < i && (i = u, r = a);
	}
	return r;
}
function Fo(e, t, n) {
	let r = e.createSVGPoint();
	r.x = t, r.y = n;
	let i = e.getScreenCTM();
	if (!i) return {
		x: 0,
		y: 0
	};
	let a = r.matrixTransform(i.inverse());
	return {
		x: a.x,
		y: a.y
	};
}
function Io(e, t, n, r) {
	let i = n - e, a = r - t, o = Math.sqrt(i * i + a * a);
	if (o === 0) return "";
	let s = -a / o, c = i / o, l = Mo / 2, u = e, d = t, f = n, p = r;
	return [
		`M ${u + s * l} ${d + c * l}`,
		`L ${f + s * l} ${p + c * l}`,
		`A ${l} ${l} 0 0 1 ${f - s * l} ${p - c * l}`,
		`L ${u - s * l} ${d - c * l}`,
		`A ${l} ${l} 0 0 1 ${u + s * l} ${d + c * l}`,
		"Z"
	].join(" ");
}
var Lo = i(({ value: e, onChange: t, onComplete: n, disabled: r = !1, error: i = !1, outerColor: o = "var(--hm-pattern-lock-outer-color, var(--harmony-icon-fourth, rgba(0, 0, 0, 0.2)))", innerColor: s = "var(--harmony-icon-primary, rgba(0, 0, 0, 0.898))", selectedInnerColor: c = "var(--harmony-brand, #0a59f7)", errorColor: f = "#e84026", lineColor: p = "var(--harmony-icon-fourth, rgba(0, 0, 0, 0.2))", className: g }, _) => {
	let v = u(null), [y, b] = d([]), [x, S] = d(-1), C = u(!1), w = e === void 0 ? y : e, T = p, E = i ? f : c, D = a((n) => {
		if (r || n < 0 || n > 8) return;
		let i = [...w, n];
		e === void 0 && b(i), t?.(i);
	}, [
		r,
		w,
		e,
		t
	]), O = a(() => {
		C.current && (C.current = !1, S(-1), w.length > 0 && n?.(w));
	}, [w, n]), k = a((n) => {
		if (r) return;
		n.preventDefault(), n.target.setPointerCapture?.(n.pointerId), C.current = !0;
		let i = [];
		e === void 0 && b(i), t?.(i);
		let a = v.current;
		if (!a) return;
		let { x: o, y: s } = Fo(a, n.clientX, n.clientY), c = Po(o, s, []);
		if (c >= 0) {
			let n = [...i, c];
			e === void 0 && b(n), t?.(n);
		}
	}, [
		r,
		e,
		t
	]), A = a((e) => {
		if (!C.current || r) return;
		e.preventDefault();
		let t = v.current;
		if (!t) return;
		let { x: n, y: i } = Fo(t, e.clientX, e.clientY), a = Po(n, i, w);
		S(a), a >= 0 && D(a);
	}, [
		r,
		w,
		D
	]), j = a((e) => {
		e.preventDefault(), e.target.releasePointerCapture?.(e.pointerId), O();
	}, [O]), M = l(() => w.map((e) => Oo[e]), [w]), N = l(() => {
		let e = [];
		for (let t = 1; t < M.length; t++) {
			let [n, r] = M[t - 1], [i, a] = M[t];
			e.push(Io(n, r, i, a));
		}
		return e;
	}, [M]), P = l(() => {
		if (!C.current || x < 0 || M.length === 0) return null;
		let e = M[M.length - 1], [t, n] = Oo[x];
		return Io(e[0], e[1], t, n);
	}, [M, x]);
	return /* @__PURE__ */ m("div", {
		ref: _,
		className: X("hm-pattern-lock inline-flex select-none", g),
		children: /* @__PURE__ */ h("svg", {
			ref: v,
			viewBox: `0 0 ${No} ${No}`,
			width: No,
			height: No,
			className: X("touch-none overflow-visible", r && "opacity-40 pointer-events-none"),
			onPointerDown: k,
			onPointerMove: A,
			onPointerUp: j,
			onPointerCancel: j,
			onPointerLeave: j,
			style: { cursor: r ? "default" : "pointer" },
			children: [
				N.map((e, t) => /* @__PURE__ */ m("path", {
					d: e,
					fill: T,
					stroke: "none"
				}, `line-${t}`)),
				P && /* @__PURE__ */ m("path", {
					d: P,
					fill: T,
					stroke: "none",
					opacity: .5
				}),
				Oo.map(([e, t], n) => {
					let r = w.includes(n);
					return /* @__PURE__ */ h("g", { children: [/* @__PURE__ */ m("circle", {
						cx: e,
						cy: t,
						r: Ao,
						fill: "none",
						stroke: o,
						strokeWidth: 2,
						opacity: r || i ? 1 : 0,
						style: { transition: "opacity 0.15s ease" }
					}), /* @__PURE__ */ m("circle", {
						cx: e,
						cy: t,
						r: r ? jo + 1 : jo,
						fill: r ? E : s,
						stroke: "none",
						style: { transition: "r 0.15s ease, fill 0.15s ease" }
					})] }, `point-${n}`);
				})
			]
		})
	});
});
Lo.displayName = "PatternLock";
//#endregion
//#region src/components/Input/PatternLock/index.ts
var Ro = /* @__PURE__ */ _({ PatternLock: () => Lo }), zo = ["OFF", "ON"], Bo = [
	"Normal",
	"Hover",
	"Press",
	"Focus",
	"Actived",
	"Typing",
	"Output",
	"icon hover",
	"icon focus",
	"icon press"
], Vo = [
	"标准",
	"强",
	"降档",
	"弱"
], Ho = [
	"Default",
	"Hover",
	"Pressed",
	"Focus"
], Uo = ["circle", "rounded"];
//#endregion
//#region src/components/Input/Search/Search.tsx
function Wo() {
	return /* @__PURE__ */ m(Z, {
		name: "magnifyingglass",
		size: 16
	});
}
function Go() {
	return /* @__PURE__ */ m(Z, {
		name: "mic",
		size: 18,
		style: { fontVariationSettings: "\"FILL\" 0, \"wght\" 400, \"GRAD\" 0, \"opsz\" 24" }
	});
}
function Ko({ Search: e = "OFF", 状态: t, 通透度: n, placeholder: r = "搜索", searchButtonText: i = "Search", value: o, onChange: s, onSearch: c, onFocus: l, onBlur: f, className: p, disabled: g, ..._ }) {
	let v = u(null), y = o !== void 0, [b, x] = d(""), S = y ? o : b, [C, w] = d("Normal"), T = (t ?? C).toLowerCase().replace(/\s+/g, "-"), E = g === !0, D = a((e) => {
		l?.(e), t || w("Focus");
	}, [l, t]), O = a((e) => {
		f?.(e), t || w((y ? o : b) !== void 0 && (y ? o : b) !== "" ? "Actived" : "Normal");
	}, [
		f,
		t,
		y,
		o,
		b
	]), k = a((e) => {
		y || x(e.target.value), s?.(e), t || w("Typing");
	}, [
		s,
		t,
		y
	]), A = a(() => {
		v.current?.focus();
	}, []), j = a((e) => {
		e.stopPropagation(), c?.(String(S ?? ""));
	}, [c, S]);
	return /* @__PURE__ */ h("div", {
		className: X("hm-search", "hm-search--type-phone", p),
		"data-search": e,
		"data-state": T,
		onClick: A,
		"aria-disabled": E || void 0,
		role: "searchbox",
		children: [
			/* @__PURE__ */ m("span", { className: "hm-search__overlay" }),
			/* @__PURE__ */ m("span", {
				className: "hm-search__icon",
				"aria-hidden": "true",
				children: /* @__PURE__ */ m(Wo, {})
			}),
			/* @__PURE__ */ m("input", {
				ref: v,
				type: "text",
				className: "hm-search__input",
				placeholder: r,
				value: S,
				onChange: k,
				onFocus: D,
				onBlur: O,
				disabled: E,
				..._
			}),
			e === "ON" && /* @__PURE__ */ h("span", {
				className: "hm-search__action",
				children: [
					/* @__PURE__ */ m("span", {
						className: "hm-search__action-voice",
						onClick: (e) => e.stopPropagation(),
						role: "button",
						tabIndex: E ? -1 : 0,
						children: /* @__PURE__ */ m(Go, {})
					}),
					/* @__PURE__ */ m($, {
						方向: "vertical",
						尺寸: "1",
						颜色: "var(--harmony-comp-background-tertiary, rgba(0, 0, 0, 0.047))",
						className: "hm-search__action-divider",
						"aria-hidden": "true"
					}),
					/* @__PURE__ */ m("span", {
						className: "hm-search__action-button",
						onClick: j,
						role: "button",
						tabIndex: E ? -1 : 0,
						children: i
					})
				]
			})
		]
	});
}
//#endregion
//#region src/components/Input/Search/Search2in1.tsx
function qo({ Search: e = "OFF", 状态: t, placeholder: n = "搜索", searchButtonText: r = "Search", value: i, onChange: o, onSearch: s, onFocus: c, onBlur: l, className: f, disabled: p, ...g }) {
	let _ = u(null), v = i !== void 0, [y, b] = d(""), x = v ? i : y, [S, C] = d("Normal"), w = (t ?? S).toLowerCase().replace(/\s+/g, "-"), T = p === !0, E = a((e) => {
		c?.(e), t || C("Focus");
	}, [c, t]), D = a((e) => {
		l?.(e), t || C((v ? i : y) !== void 0 && (v ? i : y) !== "" ? "Actived" : "Normal");
	}, [
		l,
		t,
		v,
		i,
		y
	]), O = a((e) => {
		v || b(e.target.value), o?.(e), t || C("Typing");
	}, [
		o,
		t,
		v
	]), k = a(() => {
		_.current?.focus();
	}, []), A = a((e) => {
		e.stopPropagation(), s?.(String(x ?? ""));
	}, [s, x]);
	return /* @__PURE__ */ h("div", {
		className: X("hm-search", "hm-search--type-2in1", f),
		"data-search": e,
		"data-state": w,
		onClick: k,
		"aria-disabled": T || void 0,
		role: "searchbox",
		children: [
			/* @__PURE__ */ m("span", { className: "hm-search__overlay" }),
			/* @__PURE__ */ m("span", {
				className: "hm-search__icon",
				"aria-hidden": "true",
				children: /* @__PURE__ */ m(Wo, {})
			}),
			/* @__PURE__ */ m("input", {
				ref: _,
				type: "text",
				className: "hm-search__input",
				placeholder: n,
				value: x,
				onChange: O,
				onFocus: E,
				onBlur: D,
				disabled: T,
				...g
			}),
			e === "ON" && /* @__PURE__ */ h("span", {
				className: "hm-search__action",
				children: [
					/* @__PURE__ */ m("span", {
						className: "hm-search__action-voice",
						onClick: (e) => e.stopPropagation(),
						role: "button",
						tabIndex: T ? -1 : 0,
						children: /* @__PURE__ */ m(Go, {})
					}),
					/* @__PURE__ */ m($, {
						方向: "vertical",
						尺寸: "1",
						颜色: "var(--harmony-comp-background-tertiary, rgba(0, 0, 0, 0.047))",
						className: "hm-search__action-divider",
						"aria-hidden": "true"
					}),
					/* @__PURE__ */ m("span", {
						className: "hm-search__action-button",
						onClick: A,
						role: "button",
						tabIndex: T ? -1 : 0,
						children: r
					})
				]
			})
		]
	});
}
//#endregion
//#region src/components/Input/Search/SearchIconButton.tsx
function Jo() {
	return /* @__PURE__ */ m(Z, {
		name: "chevron_left",
		size: 24
	});
}
function Yo({ 状态: e, 圆角: t = "circle", className: n, disabled: r, onClick: i, onFocus: o, onBlur: s, onMouseEnter: c, onMouseLeave: l, ...u }) {
	let f = e !== void 0, [p, g] = d("Default"), _ = f ? e : p, v = r === !0, y = a((e) => {
		i?.(e);
	}, [i]), b = a((e) => {
		o?.(e), f || g("Focus");
	}, [o, f]), x = a((e) => {
		s?.(e), f || g("Default");
	}, [s, f]), S = a((e) => {
		c?.(e), f || g("Hover");
	}, [c, f]), C = a((e) => {
		l?.(e), f || g("Default");
	}, [l, f]);
	return /* @__PURE__ */ h("button", {
		type: "button",
		className: X("hm-search-icon-button", `hm-search-icon-button--radius-${t}`, n),
		"data-state": _.toLowerCase(),
		disabled: v,
		onClick: y,
		onFocus: b,
		onBlur: x,
		onMouseEnter: S,
		onMouseLeave: C,
		...u,
		children: [/* @__PURE__ */ m("span", { className: "hm-sib__overlay" }), /* @__PURE__ */ m("span", {
			className: "hm-sib__icon",
			children: /* @__PURE__ */ m(Jo, {})
		})]
	});
}
//#endregion
//#region src/components/Input/Search/index.ts
var Xo = /* @__PURE__ */ _({
	Search: () => Ko,
	Search2in1: () => qo,
	SearchIcon: () => Wo,
	SearchIconButton: () => Yo,
	VoiceIcon: () => Go,
	searchIconButtonRadiusOptions: () => Uo,
	searchIconButtonStateOptions: () => Ho,
	searchStateOptions: () => Bo,
	searchToggleOptions: () => zo,
	searchTransparencyOptions: () => Vo
}), Zo = () => /* @__PURE__ */ m(Z, {
	name: "eye",
	size: 20,
	style: { fontVariationSettings: "\"FILL\" 0, \"wght\" 400, \"GRAD\" 0, \"opsz\" 24" }
}), Qo = () => /* @__PURE__ */ m(Z, {
	name: "eye_slash",
	size: 20,
	style: { fontVariationSettings: "\"FILL\" 0, \"wght\" 400, \"GRAD\" 0, \"opsz\" 24" }
}), $o = () => /* @__PURE__ */ m(Z, {
	name: "xmark",
	size: 18
}), es = [
	"textinput-box-phone",
	"textinput-muti-phone",
	"textinput-none-phone"
], ts = [
	"Normal",
	"Hover",
	"Focus",
	"Typing",
	"Actived",
	"Error",
	"Disable",
	"Count"
], ns = ["OFF", "ON"], rs = [
	"none",
	"1",
	"2"
];
function is(e) {
	return e.endsWith("-phone");
}
function as(e) {
	return e === "textinput-muti-phone";
}
function os({ iconType: e, customIcon: t, passwordVisible: n, onTogglePassword: r, hasValue: i, onClear: a, disabled: o }) {
	if (t) return /* @__PURE__ */ m("span", {
		className: "hm-textinput__right-icon",
		"aria-hidden": "true",
		children: t
	});
	if (e === "none") return null;
	let s = o, c = (e) => e.preventDefault();
	return e === "1" ? /* @__PURE__ */ m("button", {
		type: "button",
		className: "hm-textinput__right-icon hm-textinput__right-icon--clickable",
		onClick: s ? void 0 : r,
		onMouseDown: c,
		disabled: s,
		"aria-label": n ? "隐藏密码" : "显示密码",
		tabIndex: -1,
		children: m(n ? Qo : Zo, {})
	}) : e === "2" ? /* @__PURE__ */ h("span", {
		className: "hm-textinput__right-icon-group",
		children: [/* @__PURE__ */ m("button", {
			type: "button",
			className: "hm-textinput__right-icon hm-textinput__right-icon--clickable",
			onClick: s ? void 0 : r,
			onMouseDown: c,
			"aria-label": n ? "隐藏密码" : "显示密码",
			tabIndex: -1,
			disabled: s,
			children: m(n ? Qo : Zo, {})
		}), i && !s && /* @__PURE__ */ m("button", {
			type: "button",
			className: "hm-textinput__right-icon hm-textinput__right-icon--clickable hm-textinput__right-icon--cancel",
			onClick: a,
			onMouseDown: c,
			"aria-label": "清除输入",
			tabIndex: -1,
			children: /* @__PURE__ */ m($o, {})
		})]
	}) : null;
}
var ss = i(({ variant: e, 状态: t, 灰色场景: n = "OFF", Space: r = "OFF", icon: i = "none", rightIcon: o, errorText: s = "Error", helperText: c = "100", hintText: l = "最多 200 字", value: u, placeholder: f = "Input", onChange: p, disabled: g, rows: _ = 5, inputType: v, className: y, ...b }, x) => {
	let [S, C] = d(u ?? ""), [w, T] = d(!1), [E, D] = d(!1), O = u !== void 0, k = O ? u : S, A = t || (g ? "Disable" : w && k.length > 0 ? "Typing" : w ? "Focus" : "Normal"), j = g || A === "Disable", M = a((e) => {
		if (j) return;
		let t = e.target.value;
		p?.(t), O || C(t);
	}, [
		j,
		p,
		O
	]), N = a(() => {
		T(!0);
	}, []), P = a(() => {
		T(!1);
	}, []), F = a(() => {
		D((e) => !e);
	}, []), I = a(() => {
		C(""), p?.("");
	}, [p]), L = v || ((i === "1" || i === "2") && E ? "password" : "text"), R = "hm-textinput", z = `hm-textinput--${e}`, B = `hm-textinput--${A.toLowerCase()}`, V = is(e) && e !== "textinput-none-phone" ? `hm-textinput--gray-${n.toLowerCase()}` : "", H = e === "textinput-none-phone" ? `hm-textinput--space-${r.toLowerCase()}` : "", ee = as(e) ? "hm-textinput--multi" : "";
	if (as(e)) return /* @__PURE__ */ h("div", {
		className: X(R, z, B, V, H, ee, j && "hm-textinput--disabled", y),
		children: [/* @__PURE__ */ m("textarea", {
			ref: x,
			className: "hm-textinput__textarea",
			value: k,
			placeholder: f,
			onChange: M,
			onFocus: N,
			onBlur: P,
			disabled: j,
			rows: _,
			...b
		}), l && /* @__PURE__ */ m("span", {
			className: X("hm-textinput__hint", A === "Error" && "hm-textinput__hint--error"),
			children: l
		})]
	});
	let te = A === "Typing" || A === "Actived", U = e !== "textinput-none-phone" && (i !== "none" || !!o);
	return /* @__PURE__ */ h("div", {
		className: X(R, z, B, V, H, j && "hm-textinput--disabled", y),
		children: [/* @__PURE__ */ h("div", {
			className: "hm-textinput__field-wrapper",
			children: [
				/* @__PURE__ */ h("div", {
					className: "hm-textinput__field-inner",
					children: [te && /* @__PURE__ */ m("span", { className: X("hm-textinput__cursor", A === "Actived" && "hm-textinput__cursor--start") }), /* @__PURE__ */ m("input", {
						ref: x,
						className: "hm-textinput__input",
						type: L,
						value: k,
						placeholder: f,
						onChange: M,
						onFocus: N,
						onBlur: P,
						disabled: j,
						...b
					})]
				}),
				A === "Hover" && !j && !U && /* @__PURE__ */ m("span", { className: "hm-textinput__text-cursor" }),
				U && /* @__PURE__ */ m(os, {
					iconType: i,
					customIcon: o,
					passwordVisible: E,
					onTogglePassword: F,
					hasValue: k.length > 0,
					onClear: I,
					disabled: !!j
				})
			]
		}), (A === "Error" || A === "Count") && /* @__PURE__ */ m("span", {
			className: X("hm-textinput__helper-text", A === "Error" && "hm-textinput__helper-text--error", A === "Count" && "hm-textinput__helper-text--count"),
			children: A === "Error" ? s : `${String(k ?? "").length}/${c}`
		})]
	});
});
ss.displayName = "TextInputPrimitive";
var cs = i((e, t) => /* @__PURE__ */ m(ss, {
	...e,
	variant: "textinput-box-phone",
	ref: t
}));
cs.displayName = "TextInputBoxPhone";
var ls = i((e, t) => {
	let { icon: n, rightIcon: r, 灰色场景: i, ...a } = e;
	return /* @__PURE__ */ m(ss, {
		...a,
		variant: "textinput-none-phone",
		icon: "none",
		ref: t
	});
});
ls.displayName = "TextInputNonePhone";
var us = i((e, t) => /* @__PURE__ */ m(ss, {
	...e,
	variant: "textinput-muti-phone",
	ref: t
}));
us.displayName = "TextInputMutiPhone";
var ds = i((e, t) => {
	let n = e.类型 ?? "textinput-box-phone";
	if (n === "textinput-muti-phone") {
		let { 类型: n, ...r } = e;
		return /* @__PURE__ */ m(ss, {
			...r,
			variant: "textinput-muti-phone",
			ref: t
		});
	}
	if (n === "textinput-none-phone") {
		let { 类型: n, ...r } = e;
		return /* @__PURE__ */ m(ss, {
			...r,
			variant: "textinput-none-phone",
			ref: t
		});
	}
	let { 类型: r, ...i } = e;
	return /* @__PURE__ */ m(ss, {
		...i,
		variant: "textinput-box-phone",
		ref: t
	});
});
ds.displayName = "TextInput";
//#endregion
//#region src/components/Input/TextInput/index.ts
var fs = /* @__PURE__ */ _({
	TextInput: () => ds,
	TextInputBoxPhone: () => cs,
	TextInputMutiPhone: () => us,
	TextInputNonePhone: () => ls,
	graySceneValues: () => ns,
	rightIconTypes: () => rs,
	textInputStates: () => ts,
	textInputTypes: () => es
}), ps = (e) => typeof e == "boolean" ? `${e}` : e === 0 ? "0" : e, ms = y, hs = (e, t) => (n) => {
	if (t?.variants == null) return ms(e, n?.class, n?.className);
	let { variants: r, defaultVariants: i } = t, a = Object.keys(r).map((e) => {
		let t = n?.[e], a = i?.[e];
		if (t === null) return null;
		let o = ps(t) || ps(a);
		return r[e][o];
	}), o = n && Object.entries(n).reduce((e, t) => {
		let [n, r] = t;
		return r === void 0 || (e[n] = r), e;
	}, {});
	return ms(e, a, t?.compoundVariants?.reduce((e, t) => {
		let { class: n, className: r, ...a } = t;
		return Object.entries(a).every((e) => {
			let [t, n] = e;
			return Array.isArray(n) ? n.includes({
				...i,
				...o
			}[t]) : {
				...i,
				...o
			}[t] === n;
		}) ? [
			...e,
			n,
			r
		] : e;
	}, []), n?.class, n?.className);
}, gs = [
	"2",
	"3",
	"4",
	"5"
], _s = ["OFF", "ON"], vs = [
	"Light",
	"Dark",
	"Transparent"
], ys = ["port", "land"], bs = hs("relative inline-flex w-[360px] max-w-full flex-col text-[color:var(--harmony-font-primary)]"), xs = hs("relative flex w-full flex-col overflow-hidden bg-[color:var(--harmony-comp-background-material-tabs,var(--harmony-comp-background-gray))]", {
	variants: { layout: {
		port: "h-[76px]",
		land: "h-[68px]"
	} },
	defaultVariants: { layout: "port" }
}), Ss = hs("grid w-full place-items-stretch", {
	variants: { layout: {
		port: "h-12",
		land: "h-10"
	} },
	defaultVariants: { layout: "port" }
}), Cs = hs("flex w-full items-center justify-center", {
	variants: { layout: {
		port: "h-12",
		land: "h-10"
	} },
	defaultVariants: { layout: "port" }
}), ws = hs("group relative inline-flex h-full w-full items-center justify-center rounded-[10px] bg-transparent outline-none transition-colors focus-visible:ring-2 focus-visible:ring-[color:var(--harmony-interactive-focus)] focus-visible:ring-offset-1 focus-visible:ring-offset-[color:var(--harmony-comp-background-primary)] disabled:pointer-events-none disabled:opacity-40", {
	variants: { layout: {
		port: "flex-col gap-[2px] px-1 py-1",
		land: "flex-row gap-2 px-2 py-2"
	} },
	defaultVariants: { layout: "port" }
}), Ts = {
	Light: "bg-[rgba(0,0,0,0.2)]",
	Dark: "bg-[rgba(255,255,255,0.5)]",
	Transparent: "bg-[rgba(255,255,255,0.7)]"
}, Es = hs("truncate text-[10px] font-medium leading-[14px] tracking-[0px] [font-family:\"HarmonyHeiTi\",\"Geist_Variable\",sans-serif]", {
	variants: { layout: {
		port: "w-full text-center",
		land: "min-w-0 flex-1 text-left"
	} },
	defaultVariants: { layout: "port" }
});
function Ds(e) {
	return Array.from({ length: e }, (e, t) => ({
		key: `preview-${t + 1}`,
		label: "Tab",
		icon: /* @__PURE__ */ m(Z, {
			name: "person_crop_circle_fill_1",
			size: 24
		})
	}));
}
function Os(e) {
	return Math.min(5, Math.max(2, e));
}
function ks(e, t) {
	return e || (t === "ON" ? "land" : "port");
}
function As(e, t) {
	return e?.length ? e.length : Number(t ?? "4");
}
function js(e, t) {
	return e?.length ? e : Ds(Os(t));
}
function Ms(e, t, n) {
	return t && e.some((e) => e.key === t) ? t : n ? e.at(-1)?.key ?? e[0]?.key : e[0]?.key;
}
function Ns(e, t) {
	return t && e.some((e) => e.key === t) ? t : e[0]?.key;
}
function Ps({ active: e, item: t, layout: n, onSelect: r }) {
	let { buttonProps: i, disabled: a, icon: o, activeIcon: s, label: c } = t;
	return /* @__PURE__ */ h("button", {
		"aria-current": e ? "page" : void 0,
		"aria-label": c,
		className: ws({ layout: n }),
		"data-active": e ? "true" : "false",
		disabled: a,
		onClick: (e) => r(t, e),
		type: "button",
		...i,
		children: [/* @__PURE__ */ m("span", {
			"aria-hidden": "true",
			className: X("inline-flex size-6 shrink-0 items-center justify-center [&_svg]:size-6 [&_svg]:shrink-0", e ? "text-[color:var(--harmony-icon-emphasize)]" : "text-[color:var(--harmony-icon-secondary)]"),
			children: e ? s ?? o : o
		}), /* @__PURE__ */ m("span", {
			className: X(Es({ layout: n }), e ? "text-[color:var(--harmony-font-emphasize)]" : "text-[color:var(--harmony-font-secondary)]"),
			children: c
		})]
	});
}
function Fs({ activeKey: e, className: t, defaultActiveKey: n, indicatorMode: r = "Light", items: i, land: a, layout: o, onActiveKeyChange: s, 个数: c, ...l }) {
	let u = ks(o, a), f = js(i, As(i, c)), p = !i?.length, [g, _] = d(() => Ms(f, n, p)), v = Ns(f, e ?? g), y = (t, n) => {
		e === void 0 && _(t.key), t.onSelect?.(n), s?.(t.key, t);
	};
	return /* @__PURE__ */ m("nav", {
		"aria-label": "Bottom tab navigation",
		className: X(bs(), Q("BottomTab", {
			个数: String(c ?? f.length),
			land: a ?? "OFF",
			activeKey: v ?? ""
		}), t),
		"data-count": String(f.length),
		"data-indicator-mode": r,
		"data-land": a,
		"data-layout": u,
		...l,
		children: /* @__PURE__ */ h("div", {
			className: xs({ layout: u }),
			style: { backdropFilter: "var(--harmony-comp-background-material-tabs-blur, blur(80px))" },
			children: [/* @__PURE__ */ m("div", {
				className: Ss({ layout: u }),
				style: { gridTemplateColumns: `repeat(${f.length}, minmax(0, 1fr))` },
				children: f.map((e) => /* @__PURE__ */ m("div", {
					className: Cs({ layout: u }),
					children: /* @__PURE__ */ m(Ps, {
						active: e.key === v,
						item: e,
						layout: u,
						onSelect: y
					})
				}, e.key))
			}), /* @__PURE__ */ m("div", {
				className: "relative h-7 w-full",
				children: /* @__PURE__ */ m("span", {
					"aria-hidden": "true",
					className: X("absolute left-1/2 top-[17px] block h-[5px] w-28 -translate-x-1/2 rounded-[4px]", Ts[r])
				})
			})]
		})
	});
}
//#endregion
//#region src/components/Navigation/BottomTab/index.ts
var Is = /* @__PURE__ */ _({
	BottomTab: () => Fs,
	bottomTabCounts: () => gs,
	bottomTabIndicatorModes: () => vs,
	bottomTabLandOptions: () => _s,
	bottomTabLayouts: () => ys
}), Ls = ["activated", "enable"], Rs = [
	"默认",
	"材质-标准",
	"材质-弱",
	"材质-强",
	"材质-降档"
], zs = [
	"tab",
	"tab with icon",
	"icontab"
], Bs = [
	"强",
	"弱",
	"标准",
	"降档"
];
function Vs() {
	return /* @__PURE__ */ m(Z, {
		name: "tv",
		size: 16,
		"aria-hidden": !0
	});
}
function Hs() {
	return /* @__PURE__ */ m(Z, {
		name: "dot_grid_2x2",
		size: 24,
		"aria-hidden": !0
	});
}
function Us(e) {
	return typeof e == "string" ? /* @__PURE__ */ m(Z, {
		name: e,
		size: 16,
		"aria-hidden": !0
	}) : e;
}
function Ws({ items: e, activeKey: t, 类型: n = "tab with icon", 通透度: r = "默认", num: i = !1, icon: a, onItemSelect: o, asTabList: s = !0, className: c, ...l }) {
	let u = n === "icontab", d = !u;
	return /* @__PURE__ */ m("div", {
		className: X("pixso-chips-tab-list", Q("ChipsTab", {
			类型: n,
			通透度: r,
			num: String(i),
			icon: String(a ?? !1)
		}), c),
		role: s ? "tablist" : void 0,
		"aria-label": s ? "Chips tabs" : void 0,
		...l,
		children: e.map((e) => {
			let s = e.key === t, c = s ? e.activeIcon ?? e.icon : e.icon;
			return /* @__PURE__ */ m(Gs, {
				状态: s ? "activated" : "enable",
				通透度: r,
				类型: n,
				num: i && d,
				icon: u ? !0 : a ?? !!c,
				numValue: e.numValue,
				iconElement: c ? Us(c) : void 0,
				disabled: e.disabled,
				className: [!d && "pixso-chips-tab--icon-only", e.disabled && "pixso-chips-tab--disabled"].filter(Boolean).join(" "),
				onClick: () => o?.(e),
				children: d ? e.label : null
			}, e.key);
		})
	});
}
function Gs({ 状态: e = "enable", 通透度: t = "默认", 类型: n, num: r = !0, icon: i, numValue: a = "999", iconElement: o, children: s = "Title", className: c, "aria-selected": l, tabIndex: u, disabled: d, onClick: f, onKeyDown: p, ...g }) {
	let _ = e === "activated", v = n === "icontab", y = i ?? n !== "tab", b = r && !v, x = !v;
	return /* @__PURE__ */ h("div", {
		role: "tab",
		"aria-selected": l ?? _,
		"aria-disabled": d || void 0,
		tabIndex: u ?? (d ? -1 : _ ? 0 : -1),
		className: X("pixso-chips-tab", _ ? "pixso-chips-tab--activated" : "pixso-chips-tab--enable", v && "pixso-chips-tab--icon-only", c),
		"data-state": e,
		"data-material": t,
		"data-type": n,
		"data-num": b,
		"data-icon": y,
		onClick: d ? void 0 : f,
		onKeyDown: (e) => {
			p?.(e), !(e.defaultPrevented || d) && (e.key === "Enter" || e.key === " ") && (e.preventDefault(), e.currentTarget.click());
		},
		...g,
		children: [y ? /* @__PURE__ */ m("span", {
			className: "pixso-chips-tab__icon",
			children: o ?? /* @__PURE__ */ m(Vs, {})
		}) : null, x ? /* @__PURE__ */ h("span", {
			className: "pixso-chips-tab__text-group",
			children: [/* @__PURE__ */ m("span", {
				className: "pixso-chips-tab__title",
				children: s
			}), b && a ? /* @__PURE__ */ m("span", {
				className: "pixso-chips-tab__num",
				children: a
			}) : null]
		}) : null]
	});
}
function Ks({ items: e, activeKey: t, defaultActiveKey: n, onActiveKeyChange: r, 类型: i = "tab with icon", 通透度: a = "默认", num: o = !1, icon: s, className: c, ...l }) {
	let u = !!e?.length, [f, p] = d(() => Js(e ?? [], n));
	if (!u) return /* @__PURE__ */ m(Gs, {
		类型: i,
		通透度: a,
		num: o,
		icon: s,
		className: X(c, Q("ChipsTab", {
			类型: i,
			通透度: a,
			num: String(o ?? !1),
			icon: String(s ?? !1)
		})),
		...l
	});
	let h = t ?? f ?? n ?? e?.[0]?.key;
	return /* @__PURE__ */ m(Ws, {
		items: e ?? [],
		activeKey: h,
		类型: i,
		通透度: a,
		num: o,
		icon: s,
		onItemSelect: (e) => {
			e.disabled || (p(e.key), r?.(e.key, e));
		},
		className: c,
		...l
	});
}
function qs(e = 5) {
	return Array.from({ length: e }, (e, t) => ({
		key: `chip-${t + 1}`,
		label: "Title"
	}));
}
function Js(e, t) {
	return t && e.some((e) => e.key === t) ? t : e[0]?.key;
}
function Ys({ items: e, activeKey: t, defaultActiveKey: n, onActiveKeyChange: r, 类型: i = "tab with icon", 栏通透度: a = "标准", showMore: o = !1, onMoreClick: s, moreAriaLabel: c = "More", item通透度: l = "默认", itemNum: u = !0, itemIcon: f = !0, className: p, ...g }) {
	let _ = e?.length ? e : qs(), [v, y] = d(() => Js(_, n)), b = t !== void 0, x = b ? t : v ?? _[0]?.key, S = i === "icontab" ? !0 : f, C = i === "tab with icon", w = _.map((e) => ({
		...e,
		icon: e.icon ?? e.iconElement
	})), T = (e) => {
		e.disabled || (b || y(e.key), r?.(e.key, e));
	};
	return /* @__PURE__ */ h("nav", {
		className: X("pixso-chips-tab-phone", p),
		"data-type": i,
		"data-bar-material": a,
		"aria-label": "Chips tabs",
		...g,
		children: [/* @__PURE__ */ m("div", {
			className: `pixso-chips-tab-phone__viewport${C ? " pixso-chips-tab-phone__viewport--mask" : ""}`,
			role: "tablist",
			children: /* @__PURE__ */ m(Ws, {
				items: w,
				activeKey: x,
				类型: i,
				通透度: l,
				num: u,
				icon: S,
				onItemSelect: T,
				asTabList: !1,
				className: "pixso-chips-tab-phone__rail"
			})
		}), o ? /* @__PURE__ */ m("button", {
			type: "button",
			className: "pixso-chips-tab-phone__more",
			"aria-label": c,
			onClick: s,
			children: /* @__PURE__ */ m(Hs, {})
		}) : null]
	});
}
//#endregion
//#region src/components/Navigation/ChipsTab/index.ts
var Xs = /* @__PURE__ */ _({
	ChipsTab: () => Ks,
	ChipsTabPhone: () => Ys,
	chipsTabBarMaterials: () => Bs,
	chipsTabBarTypes: () => zs,
	chipsTabMaterials: () => Rs,
	chipsTabStates: () => Ls
}), Zs = [
	"标准",
	"强",
	"降档",
	"弱"
], Qs = [
	"tab",
	"tab with icon",
	"icontab"
];
function $s() {
	return /* @__PURE__ */ m(Z, {
		name: "dot_grid_2x2",
		size: 24,
		"aria-hidden": !0
	});
}
function ec(e) {
	return typeof e == "string" ? /* @__PURE__ */ m(Z, {
		name: e,
		size: 16,
		"aria-hidden": !0
	}) : e;
}
function tc({ active: e, state: t, icon: n, activeIcon: r, label: i, numValue: a, disabled: o, onSelect: s }) {
	let c = t ?? (e ? "activated" : "enable"), l = c === "activated", u = l ? r ?? n : n, d = !!u, f = !!a;
	return /* @__PURE__ */ h("button", {
		type: "button",
		role: "tab",
		"aria-selected": l,
		"aria-disabled": o || void 0,
		disabled: o,
		className: X("hm-floating-chips-tab-phone__chip", "hm-material-style-layer-floating-ultra-thin-effect-2", l && "hm-floating-chips-tab-phone__chip--active", o && "hm-floating-chips-tab-phone__chip--disabled"),
		"data-state": c,
		"data-icon": d,
		"data-num": f,
		onClick: o ? void 0 : s,
		children: [
			!l && /* @__PURE__ */ m("div", { className: "hm-material-style-layer hm-material-style-layer-floating-ultra-thin-fill-1" }),
			!l && /* @__PURE__ */ m("div", { className: "hm-material-style-layer hm-material-style-layer-floating-ultra-thin-fill-2" }),
			/* @__PURE__ */ m("div", { className: "hm-material-style-layer hm-material-style-layer-floating-ultra-thin-effect-1" }),
			/* @__PURE__ */ m("div", { className: "hm-material-style-layer hm-material-style-layer-floating-ultra-thin-effect-3" }),
			/* @__PURE__ */ m("div", { className: "hm-material-style-layer hm-material-style-layer-floating-ultra-thin-effect-4" }),
			/* @__PURE__ */ m("div", { className: "hm-material-style-layer hm-material-style-layer-floating-ultra-thin-effect-5" }),
			/* @__PURE__ */ m("div", { className: "hm-material-style-layer hm-material-style-layer-floating-ultra-thin-effect-6" }),
			/* @__PURE__ */ m("div", { className: "hm-material-style-layer hm-material-style-layer-floating-ultra-thin-effect-7" }),
			/* @__PURE__ */ m("div", { className: "hm-material-style-layer hm-material-style-layer-floating-ultra-thin-effect-8" }),
			d ? /* @__PURE__ */ m("span", {
				className: "hm-floating-chips-tab-phone__chip-icon",
				"aria-hidden": "true",
				children: ec(u)
			}) : null,
			/* @__PURE__ */ h("span", {
				className: "hm-floating-chips-tab-phone__text-group",
				children: [/* @__PURE__ */ m("span", {
					className: "hm-floating-chips-tab-phone__chip-label",
					children: i
				}), f ? /* @__PURE__ */ m("span", {
					className: "hm-floating-chips-tab-phone__num",
					children: a
				}) : null]
			})
		]
	});
}
function nc(e = 4) {
	return Array.from({ length: e }, (e, t) => ({
		key: `chip-${t + 1}`,
		label: "Title"
	}));
}
function rc(e, t) {
	return t && e.some((e) => e.key === t) ? t : e[0]?.key;
}
function ic({ items: e, activeKey: t, defaultActiveKey: n, onActiveKeyChange: r, 通透度: i = "标准", 类型: a = "tab", num: o = !1, icon: s = !0, 状态: c, className: l, ...u }) {
	let f = e?.length ? e : nc(), [p, g] = d(() => rc(f, n)), _ = t ?? p ?? n ?? f[0]?.key, v = a === "icontab" ? f.map((e) => ({
		...e,
		icon: e.icon ?? "star_fill"
	})) : f, y = a === "icontab" ? v.slice(0, 4) : [], b = a === "tab" || a === "icontab" || a === "tab with icon", x = a === "tab with icon", S = (e) => {
		e.disabled || (g(e.key), r?.(e.key, e));
	};
	return /* @__PURE__ */ h("div", {
		className: X("hm-floating-chips-tab-phone", l),
		"data-material": i,
		"data-type": a,
		...u,
		children: [
			/* @__PURE__ */ m("div", {
				className: X("hm-floating-chips-tab-phone__viewport", b && "hm-floating-chips-tab-phone__viewport--fade", x && "hm-floating-chips-tab-phone__viewport--fade-300"),
				role: "tablist",
				"aria-label": "Floating chips tabs",
				children: a === "icontab" ? /* @__PURE__ */ m("div", {
					className: "hm-floating-chips-tab-phone__icon-layout",
					children: y.map((e) => {
						let t = e.key === _;
						return /* @__PURE__ */ m(tc, {
							active: t,
							state: c ?? (t ? "activated" : "enable"),
							icon: s ? e.icon : void 0,
							activeIcon: s ? e.activeIcon : void 0,
							label: e.label,
							numValue: o ? e.numValue ?? "99+" : void 0,
							disabled: e.disabled,
							onSelect: () => S(e)
						}, e.key);
					})
				}) : /* @__PURE__ */ m("div", {
					className: "hm-floating-chips-tab-phone__rail",
					children: f.map((e) => {
						let t = e.key === _;
						return /* @__PURE__ */ m(tc, {
							active: t,
							state: c ?? (t ? "activated" : "enable"),
							icon: s ? e.icon : void 0,
							activeIcon: s ? e.activeIcon : void 0,
							label: e.label,
							numValue: o ? e.numValue ?? "99+" : void 0,
							disabled: e.disabled,
							onSelect: () => S(e)
						}, e.key);
					})
				})
			}),
			a === "tab with icon" ? /* @__PURE__ */ h("button", {
				type: "button",
				className: X("hm-floating-chips-tab-phone__more", "hm-material-style-layer-floating-ultra-thin-effect-2"),
				"aria-label": "更多",
				children: [
					/* @__PURE__ */ m("div", { className: "hm-material-style-layer hm-material-style-layer-floating-ultra-thin-fill-1" }),
					/* @__PURE__ */ m("div", { className: "hm-material-style-layer hm-material-style-layer-floating-ultra-thin-fill-2" }),
					/* @__PURE__ */ m("div", { className: "hm-material-style-layer hm-material-style-layer-floating-ultra-thin-effect-1" }),
					/* @__PURE__ */ m("div", { className: "hm-material-style-layer hm-material-style-layer-floating-ultra-thin-effect-3" }),
					/* @__PURE__ */ m("div", { className: "hm-material-style-layer hm-material-style-layer-floating-ultra-thin-effect-4" }),
					/* @__PURE__ */ m("div", { className: "hm-material-style-layer hm-material-style-layer-floating-ultra-thin-effect-5" }),
					/* @__PURE__ */ m("div", { className: "hm-material-style-layer hm-material-style-layer-floating-ultra-thin-effect-6" }),
					/* @__PURE__ */ m("div", { className: "hm-material-style-layer hm-material-style-layer-floating-ultra-thin-effect-7" }),
					/* @__PURE__ */ m("div", { className: "hm-material-style-layer hm-material-style-layer-floating-ultra-thin-effect-8" }),
					/* @__PURE__ */ m("span", {
						className: "hm-floating-chips-tab-phone__more-icon",
						children: /* @__PURE__ */ m($s, {})
					})
				]
			}) : null,
			a === "tab" ? /* @__PURE__ */ m("div", {
				className: "hm-floating-chips-tab-phone__fade",
				"aria-hidden": "true"
			}) : null
		]
	});
}
//#endregion
//#region src/components/Navigation/FloatingChipsTabPhone/index.ts
var ac = /* @__PURE__ */ _({
	FloatingChipsTabPhone: () => ic,
	floatingChipsTabPhoneMaterials: () => Zs,
	floatingChipsTabPhoneTypes: () => Qs
}), oc = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABcAAAAeCAYAAADHJYVoAAAB/ElEQVR4Ae3gAZAkSZIkSRKLqpm7R0REZmZmVlVVVVV3d3d3d/fMzMzMzMzMzMzMzMzMzMzMzMzMzMzMzMzMzMzMzMzMzMzMzMzMzMzMzMzMzMzMzMzMzMzMzMzMzMzMzMzMzMzMzMzMzMzMzMzMzMzMzMzMzMzMzMzMdHd3d3dXV1VVVVVmZkZGRIS7m5kKz0xmV3d1d3dPz8zMzMxMonjhemABdEAABRgBA2tgCTSeFwDi+VsAm0DHv2wJ7AONZwNAPCcB28Am/zoN2ANWXAGAeE6ngY5/uz3gEABAPNsOsMm/TwIXgBFAXLEAjvMfowFnAYsrrgEK/3H2gEMBPXCK/1gDcF7AcWDBfyyAcwJOAT3/sQB2BVwLBP+xAPYEXAsE/7EA9gVcAxT+YwHsCTgBzPmPBXBewBawzX8sgPsECLiO/1hLYFdccQro+Y9zHhjEFQU4DQT/fofAHoB4tjlwgn+fBpwFDCCe0yaww79NA84DDQBAPK8eOAEEL7oBuACYKwAQz99poONFdx4YeDYAxPN3Cuh50Z0HBp4NAPH8CQhedAmYZwNAPH9zoPKiWwKNZwNAPH87wCYvuvPAwLMBIJ6/HjjFi6YB9/GcABAv2CawwwvXgPNA4zkBIF64AiyADphzRQPWwAQcAeZ5ASBedAUIYALMCwfAPwJ3b0NYNd7t/wAAAABJRU5ErkJggg==", sc = [
	"标准",
	"强",
	"降档"
], cc = [
	"Active",
	"Defaults",
	"Indicator"
], lc = [
	"XL",
	"Large",
	"Medium",
	"Small"
], uc = [
	"OFF",
	"ON",
	"带symbol"
], dc = [
	2,
	3,
	4,
	5,
	6
], fc = [
	"hm-material-style-layer-floating-thin-fill-1",
	"hm-material-style-layer-floating-thin-fill-2",
	"hm-material-style-layer-floating-thin-effect-1",
	"hm-material-style-layer-floating-thin-effect-3",
	"hm-material-style-layer-floating-thin-effect-4",
	"hm-material-style-layer-floating-thin-effect-5",
	"hm-material-style-layer-floating-thin-effect-6",
	"hm-material-style-layer-floating-thin-effect-7",
	"hm-material-style-layer-floating-thin-effect-8"
];
function pc(e) {
	switch (e) {
		case "XL": return "active";
		case "Large": return "large";
		case "Medium": return "medium";
		case "Small": return "small";
	}
}
var mc = [
	"small",
	"medium",
	"large",
	"active",
	"large",
	"medium",
	"small"
];
function hc(e, t) {
	return Math.max(0, Math.min(e, Math.max(t - 1, 0)));
}
function gc(e, t) {
	if (e === t) return "active";
	let n = Math.abs(e - t);
	return n === 1 ? "large" : n === 2 ? "medium" : "small";
}
function _c(e, t, n, r, i) {
	if (e === "ON") {
		let e = mc.length, t = hc(n ?? 3, e);
		return Array.from({ length: e }, (e, n) => vc(gc(n, t), r, i));
	}
	let a = hc(n ?? Math.floor(t / 2), t);
	return Array.from({ length: t }, (e, t) => vc(t === a ? "active" : "large", r, i));
}
function vc(e, t, n) {
	return n == null ? yc(e, t) : pc(n);
}
function yc(e, t) {
	if (t == null) return e;
	switch (t) {
		case "Active": return "active";
		case "Defaults": return "large";
		case "Indicator": return e === "active" ? "large" : e;
	}
}
function bc(e) {
	switch (e) {
		case "标准": return "floating-swiper-dot-phone--opacity-standard";
		case "强": return "floating-swiper-dot-phone--opacity-strong";
		case "降档": return "floating-swiper-dot-phone--opacity-downshift";
	}
}
function xc({ 类型: e = "OFF", 组数: t = 5, 通透度: n = "标准", 状态: r, 尺寸: i, 活跃索引: a, onIndexChange: o, className: s, ...c }) {
	let l = _c(e, e === "带symbol" ? Math.max(t - 1, 1) : t, a, r, i), u = e === "ON" ? 7 : e === "带symbol" ? Math.max(t - 1, 1) : t, d = a === void 0 ? e === "ON" ? 3 : Math.floor(t / 2) : hc(a, u), f = n === "标准";
	return /* @__PURE__ */ m("div", {
		className: X("floating-swiper-dot-phone", bc(n), s),
		"data-type": e,
		"data-count": u,
		"data-active-index": d,
		"data-opacity": n,
		"data-state": r,
		"data-size": i,
		role: o ? "tablist" : void 0,
		...c,
		children: /* @__PURE__ */ h("div", {
			className: X("floating-swiper-dot-phone__surface", f && "hm-material-style-layer-floating-thin-effect-2"),
			children: [f ? fc.map((e) => /* @__PURE__ */ m("span", { className: X("hm-material-style-layer", e) }, e)) : null, /* @__PURE__ */ h("div", {
				className: "floating-swiper-dot-phone__content",
				children: [e === "带symbol" ? /* @__PURE__ */ m("img", {
					className: "floating-swiper-dot-phone__symbol",
					src: oc,
					alt: ""
				}) : null, /* @__PURE__ */ m("div", {
					className: "floating-swiper-dot-phone__dots",
					children: l.map((t, n) => {
						let r = X("floating-swiper-dot-phone__indicator", `floating-swiper-dot-phone__indicator--${t}`);
						return o ? /* @__PURE__ */ m("button", {
							type: "button",
							className: X("floating-swiper-dot-phone__indicator-btn", r),
							"aria-label": `第 ${n + 1} 页`,
							"aria-current": n === d ? "true" : void 0,
							onClick: () => o(n)
						}, `${e}-${n}`) : /* @__PURE__ */ m("span", { className: r }, `${e}-${n}`);
					})
				})]
			})]
		})
	});
}
//#endregion
//#region src/components/Navigation/FloatingSwiperDotPhone/index.ts
var Sc = /* @__PURE__ */ _({
	FloatingSwiperDotPhone: () => xc,
	floatingSwiperDotPhoneCounts: () => dc,
	floatingSwiperDotPhoneOpacities: () => sc,
	floatingSwiperDotPhoneSizes: () => lc,
	floatingSwiperDotPhoneStates: () => cc,
	floatingSwiperDotPhoneTypes: () => uc
}), Cc = [
	"ON",
	"OFF",
	"OFF"
], wc = [
	"hm-material-style-layer-floating-thin-fill-1",
	"hm-material-style-layer-floating-thin-fill-2",
	"hm-material-style-layer-floating-thin-effect-1",
	"hm-material-style-layer-floating-thin-effect-3",
	"hm-material-style-layer-floating-thin-effect-4",
	"hm-material-style-layer-floating-thin-effect-5",
	"hm-material-style-layer-floating-thin-effect-6",
	"hm-material-style-layer-floating-thin-effect-7",
	"hm-material-style-layer-floating-thin-effect-8"
];
function Tc(e) {
	return Array.from({ length: e }, (e, t) => ({
		key: `floating-tab-${t + 1}`,
		label: "Tab",
		icon: /* @__PURE__ */ m(Z, {
			name: "person_crop_circle_fill_1",
			size: 24
		})
	}));
}
function Ec(e, t) {
	return e || "port";
}
function Dc(e, t) {
	return e?.length ? {
		count: e.length,
		mode: "normal"
	} : t === "1+bar" ? {
		count: 1,
		mode: "expanded"
	} : t === "多+bar" ? {
		count: 4,
		mode: "collapsed"
	} : {
		count: Number(t ?? "3"),
		mode: "normal"
	};
}
function Oc(e, t) {
	return e?.length ? e : Tc(Math.min(5, Math.max(1, t)));
}
function kc(e, t) {
	return t && e.some((e) => e.key === t) ? t : e[0]?.key;
}
function Ac(e, t) {
	return t && e.some((e) => e.key === t) ? t : e[0]?.key;
}
function jc({ active: e, item: t, onSelect: n, showLabel: r }) {
	let { activeIcon: i, buttonProps: a, disabled: o, icon: s, label: c } = t;
	return /* @__PURE__ */ h("button", {
		"aria-current": e ? "page" : void 0,
		"aria-label": c,
		className: "pixso-floating-tab__item",
		"data-active": e ? "true" : "false",
		disabled: o,
		onClick: (e) => n(t, e),
		title: c,
		type: "button",
		...a,
		children: [/* @__PURE__ */ m("span", {
			className: "pixso-floating-tab__icon",
			"aria-hidden": "true",
			children: e ? i ?? s : s
		}), r ? /* @__PURE__ */ m("span", {
			className: "pixso-floating-tab__label",
			children: c
		}) : null]
	});
}
function Mc({ 歌曲标题: e = "Espressos", 封面: t, layers: n = [], transparency: r, onPlayToggle: i, onNext: a, onPrev: o }) {
	return /* @__PURE__ */ h("div", {
		className: X("pixso-floating-tab__music-pill", n.length > 0 && "hm-material-style-layer-floating-thin-effect-2"),
		"data-transparency": r,
		children: [n.map((e) => /* @__PURE__ */ m("div", { className: X("hm-material-style-layer", e) }, e)), /* @__PURE__ */ h("div", {
			className: "pixso-floating-tab__music-inner",
			children: [
				/* @__PURE__ */ m("img", {
					className: "pixso-floating-tab__music-cover",
					src: t ?? "data:image/png;base64,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",
					alt: ""
				}),
				/* @__PURE__ */ m("span", {
					className: "pixso-floating-tab__music-title",
					children: e
				}),
				/* @__PURE__ */ h("div", {
					className: "pixso-floating-tab__music-ctls",
					children: [
						/* @__PURE__ */ m("button", {
							type: "button",
							onClick: o,
							"aria-label": "上一首",
							children: /* @__PURE__ */ m(Z, {
								name: "backward_end_fill",
								size: 22
							})
						}),
						/* @__PURE__ */ m("button", {
							type: "button",
							onClick: i,
							"aria-label": "播放",
							children: /* @__PURE__ */ m(Z, {
								name: "play_fill",
								size: 22
							})
						}),
						/* @__PURE__ */ m("button", {
							type: "button",
							onClick: a,
							"aria-label": "下一首",
							children: /* @__PURE__ */ m(Z, {
								name: "forward_end_fill",
								size: 22
							})
						})
					]
				})
			]
		})]
	});
}
function Nc({ activeKey: e, className: t, defaultActiveKey: n, items: r, land: i = "OFF", layout: a, onActiveKeyChange: o, 数量: s = "3", 材质: c = "Floating_Thin", 通透度: l = "标准", 状态: u = "默认", 激活: f = Cc, 文本: p = !0, 歌曲标题: g = "Espressos", 封面: _, onPlayToggle: v, onNext: y, onPrev: b, "Color Mode": x = "Light", ...S }) {
	let C = Ec(a, i), { count: w, mode: T } = Dc(r, s), E = Oc(r, w), [D, O] = d(() => kc(E, n)), k = typeof f == "boolean" ? f ? 0 : -1 : f.findIndex((e) => e === "ON"), A = k >= 0 ? E[k]?.key : void 0, j = Ac(E, e ?? D ?? A), M = (t, n) => {
		e === void 0 && O(t.key), t.onSelect?.(n), o?.(t.key, t);
	}, N = l === "标准";
	return /* @__PURE__ */ h("div", {
		className: X("pixso-floating-tab-container", `pixso-floating-tab-container--${x.toLowerCase()}`, Q("FloatingTab", {
			数量: s,
			land: i,
			材质: c,
			通透度: l,
			状态: u,
			"Color Mode": x,
			文本: p ? "true" : "false"
		}), t),
		"data-color-mode": x,
		children: [T === "expanded" ? /* @__PURE__ */ h("div", {
			className: "pixso-floating-tab-row",
			children: [/* @__PURE__ */ m("div", {
				className: "pixso-floating-tab__music-tab",
				children: /* @__PURE__ */ h("div", {
					className: X("pixso-floating-tab__music-tab-surface", N && "hm-material-style-layer-floating-thin-effect-2"),
					"data-transparency": l,
					children: [N && wc.map((e) => /* @__PURE__ */ m("div", { className: X("hm-material-style-layer", e) }, e)), E.map((e) => /* @__PURE__ */ m(jc, {
						active: e.key === j,
						item: e,
						onSelect: M,
						showLabel: !1
					}, e.key))]
				})
			}), /* @__PURE__ */ m(Mc, {
				歌曲标题: g,
				封面: _,
				onPlayToggle: v,
				onNext: y,
				onPrev: b,
				layers: N ? wc : [],
				transparency: l
			})]
		}) : T === "collapsed" ? /* @__PURE__ */ h("div", {
			className: "pixso-floating-tab-row",
			children: [/* @__PURE__ */ m("nav", {
				"aria-label": "Floating tab navigation",
				className: "pixso-floating-tab coll-tab-bar",
				"data-count": "4",
				"data-layout": "port",
				"data-text-visible": "true",
				children: /* @__PURE__ */ h("div", {
					className: X("pixso-floating-tab__surface coll-tab-bar__surface", N && "hm-material-style-layer-floating-thin-effect-2"),
					"data-transparency": l,
					children: [N && wc.map((e) => /* @__PURE__ */ m("div", { className: X("hm-material-style-layer", e) }, e)), /* @__PURE__ */ m("div", {
						className: "pixso-floating-tab__rail coll-tab-bar__rail",
						children: E.map((e) => /* @__PURE__ */ m(jc, {
							active: e.key === j,
							item: e,
							onSelect: M,
							showLabel: !0
						}, e.key))
					})]
				})
			}), /* @__PURE__ */ h("div", {
				className: X("pixso-floating-tab__music-collapsed", N && "hm-material-style-layer-floating-thin-effect-2"),
				"data-transparency": l,
				children: [
					N && wc.map((e) => /* @__PURE__ */ m("div", { className: X("hm-material-style-layer", e) }, e)),
					/* @__PURE__ */ m("img", {
						className: "pixso-floating-tab__music-collapsed-img",
						src: _ ?? "data:image/png;base64,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",
						alt: ""
					}),
					/* @__PURE__ */ h("svg", {
						className: "pixso-floating-tab__music-collapsed-ring",
						width: "56",
						height: "56",
						viewBox: "0 0 56 56",
						"aria-hidden": "true",
						children: [/* @__PURE__ */ m("circle", {
							cx: "28",
							cy: "28",
							r: "27",
							fill: "none",
							stroke: "rgba(255,255,255,0.1)",
							strokeWidth: "2"
						}), /* @__PURE__ */ m("circle", {
							cx: "28",
							cy: "28",
							r: "27",
							fill: "none",
							stroke: "rgba(255,255,255,1)",
							strokeWidth: "2",
							strokeLinecap: "round",
							strokeDasharray: `${2 * Math.PI * 27 * .75} ${2 * Math.PI * 27 * .25}`,
							strokeDashoffset: 0
						})]
					}),
					/* @__PURE__ */ m("button", {
						type: "button",
						className: "pixso-floating-tab__music-collapsed-btn",
						onClick: v,
						"aria-label": "展开音乐"
					})
				]
			})]
		}) : /* @__PURE__ */ m("nav", {
			"aria-label": "Floating tab navigation",
			className: "pixso-floating-tab",
			"data-count": String(E.length),
			"data-layout": C,
			"data-land": i,
			"data-material": c,
			"data-transparency": l,
			"data-state": u,
			"data-text-visible": p ? "true" : "false",
			...S,
			children: /* @__PURE__ */ h("div", {
				className: X("pixso-floating-tab__surface", N && "hm-material-style-layer-floating-thin-effect-2"),
				children: [N && wc.map((e) => /* @__PURE__ */ m("div", { className: X("hm-material-style-layer", e) }, e)), /* @__PURE__ */ m("div", {
					className: "pixso-floating-tab__rail",
					style: { gridTemplateColumns: `repeat(${E.length}, minmax(0, 1fr))` },
					children: E.map((e) => /* @__PURE__ */ m(jc, {
						active: e.key === j,
						item: e,
						onSelect: M,
						showLabel: p
					}, e.key))
				})]
			})
		}), /* @__PURE__ */ m("div", {
			className: "pixso-floating-tab__bottombar",
			"aria-hidden": "true",
			children: /* @__PURE__ */ m("div", { className: "pixso-floating-tab__bottombar-pill" })
		})]
	});
}
//#endregion
//#region src/components/Navigation/FloatingTab/index.ts
var Pc = /* @__PURE__ */ _({ FloatingTab: () => Nc }), Fc = (...e) => e.filter((e, t, n) => !!e && e.trim() !== "" && n.indexOf(e) === t).join(" ").trim(), Ic = (e) => e.replace(/([a-z0-9])([A-Z])/g, "$1-$2").toLowerCase(), Lc = (e) => e.replace(/^([A-Z])|[\s-_]+(\w)/g, (e, t, n) => n ? n.toUpperCase() : t.toLowerCase()), Rc = (e) => {
	let t = Lc(e);
	return t.charAt(0).toUpperCase() + t.slice(1);
}, zc = {
	xmlns: "http://www.w3.org/2000/svg",
	width: 24,
	height: 24,
	viewBox: "0 0 24 24",
	fill: "none",
	stroke: "currentColor",
	strokeWidth: 2,
	strokeLinecap: "round",
	strokeLinejoin: "round"
}, Bc = (e) => {
	for (let t in e) if (t.startsWith("aria-") || t === "role" || t === "title") return !0;
	return !1;
}, Vc = n({}), Hc = () => o(Vc), Uc = i(({ color: e, size: t, strokeWidth: n, absoluteStrokeWidth: i, className: a = "", children: o, iconNode: s, ...c }, l) => {
	let { size: u = 24, strokeWidth: d = 2, absoluteStrokeWidth: f = !1, color: p = "currentColor", className: m = "" } = Hc() ?? {}, h = i ?? f ? Number(n ?? d) * 24 / Number(t ?? u) : n ?? d;
	return r("svg", {
		ref: l,
		...zc,
		width: t ?? u ?? zc.width,
		height: t ?? u ?? zc.height,
		stroke: e ?? p,
		strokeWidth: h,
		className: Fc("lucide", m, a),
		...!o && !Bc(c) && { "aria-hidden": "true" },
		...c
	}, [...s.map(([e, t]) => r(e, t)), ...Array.isArray(o) ? o : [o]]);
}), Wc = (e, t) => {
	let n = i(({ className: n, ...i }, a) => r(Uc, {
		ref: a,
		iconNode: t,
		className: Fc(`lucide-${Ic(Rc(e))}`, `lucide-${e}`, n),
		...i
	}));
	return n.displayName = Rc(e), n;
}, Gc = Wc("chevron-left", [["path", {
	d: "m15 18-6-6 6-6",
	key: "1wnfg3"
}]]), Kc = Wc("circle-dashed", [
	["path", {
		d: "M10.1 2.182a10 10 0 0 1 3.8 0",
		key: "5ilxe3"
	}],
	["path", {
		d: "M13.9 21.818a10 10 0 0 1-3.8 0",
		key: "11zvb9"
	}],
	["path", {
		d: "M17.609 3.721a10 10 0 0 1 2.69 2.7",
		key: "1iw5b2"
	}],
	["path", {
		d: "M2.182 13.9a10 10 0 0 1 0-3.8",
		key: "c0bmvh"
	}],
	["path", {
		d: "M20.279 17.609a10 10 0 0 1-2.7 2.69",
		key: "1ruxm7"
	}],
	["path", {
		d: "M21.818 10.1a10 10 0 0 1 0 3.8",
		key: "qkgqxc"
	}],
	["path", {
		d: "M3.721 6.391a10 10 0 0 1 2.7-2.69",
		key: "1mcia2"
	}],
	["path", {
		d: "M6.391 20.279a10 10 0 0 1-2.69-2.7",
		key: "1fvljs"
	}]
]), qc = Wc("list", [
	["path", {
		d: "M3 5h.01",
		key: "18ugdj"
	}],
	["path", {
		d: "M3 12h.01",
		key: "nlz23k"
	}],
	["path", {
		d: "M3 19h.01",
		key: "noohij"
	}],
	["path", {
		d: "M8 5h13",
		key: "1pao27"
	}],
	["path", {
		d: "M8 12h13",
		key: "1za7za"
	}],
	["path", {
		d: "M8 19h13",
		key: "m83p4d"
	}]
]), Jc = [
	"1",
	"2",
	"3"
];
function Yc({ 类型: e = "1", ...t }) {
	return /* @__PURE__ */ m("svg", {
		width: 26,
		height: 13,
		viewBox: "0 0 26 13",
		fill: "none",
		"aria-hidden": "true",
		...t,
		children: e === "1" ? /* @__PURE__ */ h(p, { children: [
			/* @__PURE__ */ m("path", {
				d: "M17.4878 0L5.76024 0C3.74406 0 2.73596 0 1.96588 0.392376C1.28849 0.73752 0.737764 1.28825 0.39262 1.96563C0.000244141 2.73572 0.000244141 3.74381 0.000244141 5.76L0.000244141 7.24C0.000244141 9.25619 0.000244141 10.2643 0.39262 11.0344C0.737765 11.7118 1.28849 12.2625 1.96588 12.6076C2.73596 13 3.74405 13 5.76024 13L17.4878 13C19.504 13 20.5121 13 21.2822 12.6076C21.9596 12.2625 22.5103 11.7117 22.8554 11.0344C23.2478 10.2643 23.2478 9.25619 23.2478 7.24L23.2478 5.76C23.2478 3.74381 23.2478 2.73571 22.8554 1.96563C22.5103 1.28825 21.9596 0.73752 21.2822 0.392376C20.5121 0 19.504 0 17.4878 0ZM25 4.5C24.5858 4.5 24.25 4.83579 24.25 5.25L24.25 7.75C24.25 8.16421 24.5858 8.5 25 8.5C25.4142 8.5 25.75 8.16421 25.75 7.75L25.75 5.25C25.75 4.83579 25.4142 4.5 25 4.5Z",
				fill: "currentColor",
				fillOpacity: "0.1",
				fillRule: "evenodd"
			}),
			/* @__PURE__ */ m("path", {
				d: "M5.76024 0L17.4878 0C19.504 0 20.5121 0 21.2822 0.392376C21.9596 0.73752 22.5103 1.28825 22.8554 1.96563C23.2478 2.73571 23.2478 3.74381 23.2478 5.76L23.2478 7.24C23.2478 9.25619 23.2478 10.2643 22.8554 11.0344C22.5103 11.7117 21.9596 12.2625 21.2822 12.6076C20.5121 13 19.504 13 17.4878 13L5.76024 13C3.74405 13 2.73596 13 1.96588 12.6076C1.28849 12.2625 0.737765 11.7118 0.39262 11.0344C0.000244141 10.2643 0.000244141 9.25619 0.000244141 7.24L0.000244141 5.76C0.000244141 3.74381 0.000244141 2.73572 0.39262 1.96563C0.737764 1.28825 1.28849 0.73752 1.96588 0.392376C2.73596 0 3.74406 0 5.76024 0ZM17.4878 1L5.76024 1Q4.82302 1 4.4408 1.00601Q3.8496 1.0153 3.4772 1.04573Q2.77345 1.10322 2.41987 1.28338Q2.23642 1.37686 2.0719 1.49639L2.07166 1.49656Q1.90726 1.61603 1.76177 1.76152Q1.61617 1.90711 1.49664 2.07164L1.49664 2.07164Q1.3771 2.23617 1.28363 2.41962Q1.10347 2.7732 1.04597 3.47696Q1.01554 3.84936 1.00625 4.44056Q1.00024 4.82277 1.00024 5.76L1.00024 7.24Q1.00024 8.17723 1.00625 8.55944Q1.01554 9.15064 1.04597 9.52304C1.0843 9.99221 1.16352 10.3447 1.28363 10.5804C1.40826 10.825 1.56764 11.0444 1.76177 11.2385C1.95589 11.4326 2.17526 11.592 2.41987 11.7166C2.65559 11.8367 3.00803 11.9159 3.4772 11.9543C3.72547 11.9746 4.04667 11.9878 4.4408 11.994Q4.82306 12 5.76024 12L17.4878 12C18.1126 12 18.5525 11.998 18.8072 11.994C19.2014 11.9878 19.5226 11.9746 19.7708 11.9543C20.24 11.9159 20.5925 11.8367 20.8282 11.7166C21.0728 11.592 21.2922 11.4326 21.4863 11.2385C21.6804 11.0444 21.8398 10.825 21.9644 10.5804C22.0845 10.3447 22.1637 9.99221 22.2021 9.52304C22.2224 9.27475 22.2356 8.95355 22.2418 8.55944Q22.2478 8.17728 22.2478 7.24L22.2478 5.76Q22.2478 4.82272 22.2418 4.44056C22.2356 4.04645 22.2224 3.72525 22.2021 3.47696C22.1637 3.00779 22.0845 2.65534 21.9644 2.41962Q21.8712 2.23668 21.7521 2.07255L21.7503 2.07016Q21.6312 1.90645 21.4863 1.76152C21.2922 1.5674 21.0728 1.40802 20.8282 1.28338C20.5925 1.16328 20.24 1.08406 19.7708 1.04573C19.5226 1.02544 19.2014 1.0122 18.8072 1.00601C18.5524 1.002 18.1126 1 17.4878 1ZM24.25 5.25C24.25 4.83579 24.5858 4.5 25 4.5C25.4142 4.5 25.75 4.83579 25.75 5.25L25.75 7.75C25.75 8.16421 25.4142 8.5 25 8.5C24.5858 8.5 24.25 8.16421 24.25 7.75L24.25 5.25Z",
				fill: "currentColor",
				fillOpacity: "0.898",
				fillRule: "evenodd"
			}),
			/* @__PURE__ */ m("path", {
				d: "M14.1433 5.09144C14.1579 5.45811 14.1653 5.97878 14.1653 6.65344C14.1653 7.15211 14.1579 7.57011 14.1433 7.90744C14.1066 8.43544 13.9746 8.90844 13.7473 9.32644C13.5199 9.74444 13.2064 10.0726 12.8068 10.3109C12.7767 10.3289 12.7463 10.3461 12.7155 10.3627L12.7154 10.3627C12.3369 10.5665 11.9035 10.6684 11.4153 10.6684C10.8983 10.6684 10.4446 10.5573 10.0542 10.3351C10.0403 10.3272 10.0265 10.3191 10.0128 10.3109C9.84474 10.2108 9.69195 10.0947 9.55439 9.96274C9.36473 9.78082 9.20402 9.56872 9.07225 9.32644C8.84492 8.90845 8.71659 8.43544 8.68725 7.90744C8.67259 7.54078 8.66525 7.06411 8.66525 6.47744C8.66525 5.89078 8.67259 5.42878 8.68725 5.09144C8.71659 4.56344 8.84492 4.09044 9.07225 3.67244C9.20401 3.43017 9.36472 3.21808 9.55438 3.03616L9.55439 3.03615L9.5545 3.03604C9.69203 2.90414 9.84478 2.78811 10.0128 2.68794C10.0263 2.67984 10.04 2.67188 10.0537 2.66405L10.0541 2.66382L10.0542 2.66381C10.4446 2.44157 10.8983 2.33044 11.4153 2.33044C11.9035 2.33044 12.3369 2.43236 12.7155 2.63618L12.7156 2.63626C12.7464 2.65282 12.7767 2.67005 12.8068 2.68794C12.9747 2.78808 13.1274 2.90407 13.2649 3.03592L13.2651 3.03615L13.2652 3.03619C13.4548 3.2181 13.6155 3.43019 13.7473 3.67244C13.9746 4.09044 14.1066 4.56344 14.1433 5.09144ZM20.5559 6.65344C20.5559 5.97878 20.5485 5.45811 20.5339 5.09144C20.4972 4.56344 20.3652 4.09044 20.1379 3.67244C20.0061 3.43017 19.8454 3.21807 19.6557 3.03615L19.6557 3.03613C19.5182 2.90419 19.3654 2.78813 19.1974 2.68794C19.1674 2.67005 19.137 2.65282 19.1062 2.63626L19.1061 2.63618C18.7276 2.43236 18.2942 2.33044 17.8059 2.33044C17.2889 2.33044 16.8352 2.44157 16.4448 2.66382L16.4444 2.66405C16.4306 2.67188 16.417 2.67984 16.4034 2.68794C16.2354 2.78813 16.0826 2.90419 15.945 3.03613L15.945 3.03615L15.945 3.03617C15.7553 3.21808 15.5946 3.43018 15.4629 3.67244C15.2355 4.09044 15.1072 4.56344 15.0779 5.09144C15.0632 5.42878 15.0559 5.89078 15.0559 6.47744C15.0559 7.06411 15.0632 7.54078 15.0779 7.90744C15.1072 8.43544 15.2355 8.90845 15.4629 9.32644C15.5946 9.56872 15.7554 9.78082 15.945 9.96274L15.945 9.96275C16.0826 10.0947 16.2354 10.2108 16.4034 10.3109C16.4171 10.3191 16.4309 10.3272 16.4448 10.3351C16.8352 10.5573 17.2889 10.6684 17.8059 10.6684C18.2941 10.6684 18.7275 10.5665 19.1061 10.3627C19.1369 10.3461 19.1673 10.3289 19.1974 10.3109C19.597 10.0726 19.9105 9.74444 20.1379 9.32644C20.3652 8.90844 20.4972 8.43544 20.5339 7.90744C20.5485 7.57011 20.5559 7.15211 20.5559 6.65344ZM2.86912 3.77204C2.75178 3.83804 2.69312 3.94437 2.69312 4.09104L2.69312 5.03704C2.69312 5.14256 2.71821 5.21357 2.76841 5.25008C2.79495 5.26939 2.82852 5.27904 2.86912 5.27904C2.90505 5.27904 2.93739 5.27185 2.96614 5.25748C2.97846 5.25132 2.99012 5.24384 3.00112 5.23504L4.78312 4.24504L4.78312 10.273C4.78312 10.3537 4.80695 10.4179 4.85462 10.4655C4.90228 10.5132 4.96645 10.537 5.04712 10.537L6.13612 10.537C6.21678 10.537 6.28095 10.5132 6.32862 10.4655C6.37628 10.4179 6.40012 10.3537 6.40012 10.273L6.40012 2.74904C6.40012 2.68515 6.38517 2.63162 6.35527 2.58843C6.34741 2.57708 6.33853 2.56646 6.32862 2.55654C6.28095 2.50887 6.21678 2.48504 6.13612 2.48504L5.33312 2.48504C5.22715 2.48504 5.13178 2.50623 5.04701 2.54862L5.04698 2.54864L5.04695 2.54865C5.03201 2.55612 5.0174 2.56425 5.00312 2.57304L2.86912 3.77204ZM12.5478 6.4994C12.5478 7.2034 12.5441 7.62506 12.5368 7.7644C12.5148 8.23373 12.4048 8.59306 12.2068 8.8424C12.1172 8.95524 12.014 9.04255 11.8974 9.10433L11.8973 9.10437C11.7562 9.17905 11.5954 9.2164 11.4148 9.2164C11.2178 9.2164 11.0452 9.1739 10.897 9.0889L10.897 9.08889C10.7914 9.02831 10.6981 8.94615 10.6173 8.8424C10.4229 8.59306 10.3148 8.23373 10.2928 7.7644C10.2854 7.62506 10.2818 7.2034 10.2818 6.4994C10.2818 5.78806 10.2854 5.3664 10.2928 5.2344C10.3148 4.7724 10.4229 4.41673 10.6173 4.1674C10.6981 4.06365 10.7914 3.98148 10.897 3.9209C11.0452 3.8359 11.2178 3.7934 11.4148 3.7934C11.5954 3.7934 11.7562 3.83074 11.8973 3.90542C12.014 3.9672 12.1171 4.05452 12.2068 4.1674C12.4048 4.41673 12.5148 4.7724 12.5368 5.2344C12.5441 5.3664 12.5478 5.78806 12.5478 6.4994ZM18.9274 7.7644C18.9347 7.62506 18.9384 7.2034 18.9384 6.4994C18.9384 5.78806 18.9347 5.3664 18.9274 5.2344C18.9054 4.7724 18.7954 4.41673 18.5974 4.1674C18.5078 4.05452 18.4046 3.9672 18.2879 3.90542C18.1468 3.83074 17.986 3.7934 17.8054 3.7934C17.6084 3.7934 17.4358 3.8359 17.2876 3.9209C17.182 3.98148 17.0888 4.06365 17.0079 4.1674C16.8136 4.41673 16.7054 4.7724 16.6834 5.2344C16.6761 5.3664 16.6724 5.78806 16.6724 6.4994C16.6724 7.2034 16.6761 7.62506 16.6834 7.7644C16.7054 8.23373 16.8136 8.59306 17.0079 8.8424C17.0888 8.94615 17.182 9.02831 17.2876 9.08889C17.4358 9.17389 17.6084 9.2164 17.8054 9.2164C17.986 9.2164 18.1468 9.17905 18.2879 9.10437C18.4046 9.04259 18.5078 8.95527 18.5974 8.8424C18.7954 8.59306 18.9054 8.23373 18.9274 7.7644Z",
				fill: "currentColor",
				fillOpacity: "0.898",
				fillRule: "evenodd"
			})
		] }) : e === "2" ? /* @__PURE__ */ h(p, { children: [
			/* @__PURE__ */ m("path", {
				d: "M5.76049 0L17.488 0C19.5042 0 20.5123 0 21.2824 0.392376C21.9598 0.73752 22.5105 1.28825 22.8557 1.96563C23.248 2.73571 23.248 3.74381 23.248 5.76L23.248 7.24C23.248 9.25619 23.248 10.2643 22.8557 11.0344C22.5105 11.7117 21.9598 12.2625 21.2824 12.6076C20.5123 13 19.5042 13 17.488 13L5.76049 13C3.7443 13 2.7362 13 1.96612 12.6076C1.28874 12.2625 0.738009 11.7118 0.392864 11.0344C0.000488281 10.2643 0.000488281 9.25619 0.000488281 7.24L0.000488281 5.76C0.000488281 3.74381 0.000488281 2.73572 0.392864 1.96563C0.738008 1.28825 1.28874 0.73752 1.96612 0.392376C2.7362 0 3.7443 0 5.76049 0ZM17.488 1L5.76049 1Q4.82326 1 4.44105 1.00601Q3.84985 1.0153 3.47745 1.04573Q2.77369 1.10322 2.42011 1.28338Q2.23666 1.37686 2.07214 1.49639L2.0719 1.49656Q1.9075 1.61603 1.76201 1.76152Q1.61642 1.90711 1.49688 2.07164L1.49688 2.07164Q1.37735 2.23617 1.28387 2.41962Q1.10371 2.7732 1.04621 3.47696Q1.01579 3.84936 1.0065 4.44056Q1.00049 4.82277 1.00049 5.76L1.00049 7.24Q1.00049 8.17723 1.0065 8.55944Q1.01579 9.15064 1.04621 9.52304C1.08455 9.99221 1.16377 10.3447 1.28387 10.5804C1.40851 10.825 1.56789 11.0444 1.76201 11.2385C1.95613 11.4326 2.1755 11.592 2.42011 11.7166C2.65583 11.8367 3.00828 11.9159 3.47745 11.9543C3.72572 11.9746 4.04692 11.9878 4.44105 11.994Q4.8233 12 5.76049 12L17.488 12C18.1129 12 18.5527 11.998 18.8075 11.994C19.2016 11.9878 19.5228 11.9746 19.7711 11.9543C20.2403 11.9159 20.5927 11.8367 20.8284 11.7166C21.073 11.592 21.2924 11.4326 21.4865 11.2385C21.6807 11.0444 21.84 10.825 21.9647 10.5804C22.0848 10.3447 22.164 9.99221 22.2023 9.52304C22.2226 9.27475 22.2358 8.95355 22.242 8.55944Q22.248 8.17728 22.248 7.24L22.248 5.76Q22.248 4.82272 22.242 4.44056C22.2358 4.04645 22.2226 3.72525 22.2023 3.47696C22.164 3.00779 22.0848 2.65534 21.9647 2.41962Q21.8715 2.23668 21.7523 2.07255L21.7506 2.07016Q21.6315 1.90645 21.4865 1.76152C21.2924 1.5674 21.073 1.40802 20.8284 1.28338C20.5927 1.16328 20.2403 1.08406 19.7711 1.04573C19.5228 1.02544 19.2016 1.0122 18.8075 1.00601C18.5527 1.002 18.1129 1 17.488 1ZM24.2502 5.25C24.2502 4.83579 24.586 4.5 25.0002 4.5C25.4145 4.5 25.7502 4.83579 25.7502 5.25L25.7502 7.75C25.7502 8.16421 25.4145 8.5 25.0002 8.5C24.586 8.5 24.2502 8.16421 24.2502 7.75L24.2502 5.25Z",
				fill: "currentColor",
				fillOpacity: "0.898",
				fillRule: "evenodd"
			}),
			/* @__PURE__ */ m("rect", {
				x: 2,
				y: 2,
				width: 19.25,
				height: 9,
				rx: 1.5,
				fill: "currentColor",
				fillOpacity: "0.098"
			}),
			/* @__PURE__ */ m("path", {
				d: "M13.7354 5.14037C13.7487 5.4737 13.7554 5.94704 13.7554 6.56037C13.7554 7.0137 13.7487 7.3937 13.7354 7.70037C13.702 8.18037 13.582 8.61037 13.3754 8.99037C13.2556 9.21062 13.1095 9.40343 12.9371 9.56881L12.9371 9.56882L12.937 9.56891C12.8119 9.68882 12.6731 9.79431 12.5204 9.88537C12.4931 9.90166 12.4654 9.91734 12.4374 9.93241L12.4374 9.93243L12.4373 9.93248C12.0932 10.1177 11.6992 10.2104 11.2554 10.2104C10.7854 10.2104 10.373 10.1094 10.018 9.90732L10.018 9.9073L10.0177 9.90714L10.0167 9.90653L10.0157 9.90596C10.0038 9.89921 9.99207 9.89235 9.98037 9.88537C9.82763 9.79429 9.68873 9.68877 9.56367 9.56882C9.39126 9.40344 9.24516 9.21062 9.12537 8.99037C8.9187 8.61037 8.80204 8.18037 8.77537 7.70037C8.76204 7.36704 8.75537 6.9337 8.75537 6.40037C8.75537 5.86704 8.76204 5.44704 8.77537 5.14037C8.80204 4.66037 8.9187 4.23037 9.12537 3.85037C9.24516 3.63012 9.39126 3.4373 9.56368 3.27192L9.56369 3.27191C9.68874 3.15197 9.82763 3.04645 9.98037 2.95537C9.99275 2.94799 10.0052 2.94073 10.0177 2.9336L10.018 2.93344C10.373 2.7314 10.7854 2.63037 11.2554 2.63037C11.6992 2.63037 12.0932 2.72301 12.4374 2.90829L12.4374 2.90831C12.4654 2.92338 12.493 2.93907 12.5204 2.95537C12.6731 3.04645 12.812 3.15197 12.9371 3.27192L12.9371 3.27193C13.1095 3.43731 13.2556 3.63012 13.3754 3.85037C13.582 4.23037 13.702 4.66037 13.7354 5.14037ZM19.5654 6.56037C19.5654 5.94704 19.5588 5.4737 19.5454 5.14037C19.5121 4.66037 19.3921 4.23037 19.1854 3.85037C19.0656 3.63012 18.9195 3.43731 18.7471 3.27193L18.7471 3.27192C18.6221 3.15197 18.4832 3.04645 18.3304 2.95537C18.3031 2.93907 18.2754 2.92338 18.2474 2.90831C17.9033 2.72302 17.5093 2.63037 17.0654 2.63037C16.5955 2.63037 16.183 2.7314 15.8281 2.93344L15.8278 2.9336C15.8153 2.94073 15.8028 2.94799 15.7904 2.95537C15.6377 3.04646 15.4988 3.15197 15.3737 3.27192C15.2013 3.43731 15.0552 3.63012 14.9354 3.85037C14.7288 4.23037 14.6121 4.66037 14.5854 5.14037C14.5721 5.44704 14.5654 5.86704 14.5654 6.40037C14.5654 6.9337 14.5721 7.36704 14.5854 7.70037C14.6121 8.18037 14.7288 8.61037 14.9354 8.99037C15.0552 9.21062 15.2013 9.40343 15.3737 9.56881L15.3737 9.56882C15.4988 9.68877 15.6377 9.79429 15.7904 9.88537C15.8019 9.89219 15.8134 9.89891 15.8249 9.90552L15.8278 9.90714L15.8281 9.9073C16.183 10.1093 16.5955 10.2104 17.0654 10.2104C17.5093 10.2104 17.9033 10.1177 18.2474 9.93243L18.2475 9.93241C18.2755 9.91734 18.3031 9.90166 18.3304 9.88537C18.4831 9.79431 18.622 9.68882 18.747 9.56891L18.7471 9.56882L18.7471 9.56881C18.9195 9.40343 19.0656 9.21062 19.1854 8.99037C19.3921 8.61037 19.5121 8.18037 19.5454 7.70037C19.5588 7.3937 19.5654 7.0137 19.5654 6.56037ZM3.48526 3.94029C3.37859 4.00029 3.32526 4.09695 3.32526 4.23029L3.32526 5.09029C3.32526 5.18621 3.34807 5.25077 3.3937 5.28396C3.41784 5.30151 3.44836 5.31029 3.48526 5.31029C3.51792 5.31029 3.54732 5.30375 3.57346 5.29069L3.57348 5.29067C3.58467 5.28507 3.59526 5.27828 3.60526 5.27029L5.22526 4.37029L5.22526 9.85029C5.22526 9.90837 5.23885 9.95704 5.26603 9.9963L5.26604 9.99631C5.27317 10.0066 5.28125 10.0163 5.29026 10.0253C5.33359 10.0686 5.39192 10.0903 5.46526 10.0903L6.45526 10.0903C6.52859 10.0903 6.58692 10.0686 6.63026 10.0253C6.63927 10.0163 6.64735 10.0066 6.65448 9.9963C6.68167 9.95704 6.69526 9.90836 6.69526 9.85029L6.69526 3.01029C6.69526 2.95221 6.68167 2.90354 6.65448 2.86427L6.65446 2.86424C6.64733 2.85394 6.63926 2.84429 6.63026 2.83529C6.58692 2.79195 6.52859 2.77029 6.45526 2.77029L5.72526 2.77029C5.62892 2.77029 5.54222 2.78955 5.46516 2.82809L5.46515 2.82809L5.46514 2.82809C5.45155 2.83489 5.43825 2.84229 5.42526 2.85029L3.48526 3.94029ZM12.2844 6.42021C12.2844 7.0602 12.2811 7.44354 12.2744 7.5702C12.2544 7.99687 12.1544 8.32354 11.9744 8.55021C11.8929 8.65281 11.7991 8.73219 11.6931 8.78835L11.693 8.78836C11.5648 8.85626 11.4186 8.89021 11.2544 8.89021C11.0753 8.89021 10.9184 8.85157 10.7837 8.77429L10.7837 8.77429L10.7837 8.77429C10.6877 8.71921 10.6029 8.64452 10.5294 8.55021C10.3527 8.32354 10.2544 7.99687 10.2344 7.5702C10.2277 7.44354 10.2244 7.0602 10.2244 6.42021C10.2244 5.77354 10.2277 5.3902 10.2344 5.27021C10.2544 4.85021 10.3527 4.52687 10.5294 4.30021C10.6029 4.20591 10.6876 4.13122 10.7836 4.07615L10.7837 4.07612C10.9184 3.99884 11.0753 3.96021 11.2544 3.96021C11.4186 3.96021 11.5648 3.99415 11.693 4.06205C11.7991 4.11821 11.8929 4.19759 11.9744 4.30021C12.1544 4.52687 12.2544 4.85021 12.2744 5.27021C12.2811 5.3902 12.2844 5.77354 12.2844 6.42021ZM18.0845 7.5702C18.0911 7.44354 18.0945 7.0602 18.0945 6.42021C18.0945 5.77354 18.0911 5.3902 18.0845 5.27021C18.0645 4.85021 17.9645 4.52687 17.7845 4.30021C17.703 4.19759 17.6092 4.11821 17.5031 4.06205C17.3749 3.99415 17.2286 3.96021 17.0645 3.96021C16.8854 3.96021 16.7285 3.99884 16.5938 4.07612C16.4977 4.13119 16.413 4.20589 16.3395 4.30021C16.1628 4.52687 16.0645 4.85021 16.0445 5.27021C16.0378 5.3902 16.0345 5.77354 16.0345 6.42021C16.0345 7.0602 16.0378 7.44354 16.0445 7.5702C16.0645 7.99687 16.1628 8.32354 16.3395 8.55021C16.413 8.64452 16.4977 8.71921 16.5938 8.77429C16.7285 8.85157 16.8854 8.89021 17.0645 8.89021C17.2286 8.89021 17.3749 8.85626 17.5031 8.78836C17.6092 8.7322 17.703 8.65282 17.7845 8.55021C17.9645 8.32354 18.0645 7.99687 18.0845 7.5702Z",
				fill: "currentColor",
				fillOpacity: "0.898",
				fillRule: "evenodd"
			})
		] }) : /* @__PURE__ */ m("path", {
			d: "M17.4903 0L5.7627 0C3.74651 0 2.73842 0 1.96833 0.392376C1.29095 0.73752 0.740221 1.28825 0.395077 1.96563C0.00270081 2.73572 0.00270081 3.74381 0.00270081 5.76L0.00270081 7.24C0.00270081 9.25619 0.00270081 10.2643 0.395077 11.0344C0.740221 11.7118 1.29095 12.2625 1.96833 12.6076C2.73842 13 3.74651 13 5.7627 13L17.4903 13C19.5065 13 20.5145 13 21.2846 12.6076C21.962 12.2625 22.5127 11.7117 22.8579 11.0344C23.2503 10.2643 23.2503 9.25619 23.2503 7.24L23.2503 5.76C23.2503 3.74381 23.2503 2.73571 22.8579 1.96563C22.5127 1.28825 21.962 0.73752 21.2846 0.392376C20.5145 0 19.5065 0 17.4903 0ZM13.9877 6.52774C13.9877 5.89524 13.9809 5.40711 13.9671 5.06336C13.9327 4.56836 13.809 4.12492 13.5959 3.73305C13.4723 3.50591 13.3217 3.30707 13.1439 3.13652L13.1437 3.13634L13.1437 3.13633C13.0147 3.01271 12.8716 2.90396 12.7141 2.81008C12.6866 2.79365 12.6587 2.77782 12.6305 2.76259L12.6291 2.76184L12.6286 2.76159L12.6286 2.76155L12.6285 2.76151C12.2736 2.57045 11.8673 2.47492 11.4096 2.47492C10.925 2.47492 10.4996 2.5791 10.1336 2.78745L10.1336 2.78747C10.1206 2.79487 10.1076 2.80241 10.0948 2.81008C9.93725 2.90401 9.79401 3.01283 9.66505 3.13652C9.48723 3.30708 9.33657 3.50592 9.21305 3.73305C8.99992 4.12492 8.87961 4.56836 8.85211 5.06336C8.83836 5.37961 8.83148 5.81274 8.83148 6.36274C8.83148 6.91274 8.83836 7.35961 8.85211 7.70336C8.87961 8.19836 8.99992 8.6418 9.21305 9.03367C9.33657 9.2608 9.48723 9.45963 9.66502 9.63017L9.66504 9.63019L9.66519 9.63034L9.66521 9.63035C9.79413 9.75399 9.93732 9.86275 10.0948 9.95664C10.1076 9.96431 10.1206 9.97185 10.1336 9.97926L10.1336 9.97927C10.4996 10.1876 10.925 10.2918 11.4096 10.2918C11.8674 10.2918 12.2737 10.1963 12.6285 10.0052L12.6287 10.0051L12.6292 10.0048L12.6297 10.0046C12.6582 9.98921 12.6863 9.97323 12.7141 9.95664C12.8716 9.86273 13.0148 9.75395 13.1438 9.63028L13.1439 9.6302C13.3217 9.45965 13.4723 9.26081 13.5959 9.03367C13.809 8.6418 13.9327 8.19836 13.9671 7.70336C13.9809 7.38711 13.9877 6.99524 13.9877 6.52774ZM19.9588 5.06336C19.9726 5.40711 19.9794 5.89524 19.9794 6.52774C19.9794 6.99524 19.9726 7.38711 19.9588 7.70336C19.9244 8.19836 19.8007 8.6418 19.5876 9.03367C19.464 9.2608 19.3134 9.45963 19.1356 9.6302L19.1355 9.63028C19.0065 9.75395 18.8633 9.86273 18.7058 9.95664C18.6779 9.97332 18.6496 9.98938 18.6209 10.0048L18.6204 10.0051L18.6202 10.0052C18.2654 10.1963 17.8591 10.2918 17.4013 10.2918C16.9167 10.2918 16.4913 10.1876 16.1253 9.97926C16.1123 9.97185 16.0993 9.96431 16.0865 9.95664C15.929 9.86275 15.7858 9.75398 15.6569 9.63034L15.6567 9.63019L15.6567 9.63018C15.4789 9.45964 15.3283 9.2608 15.2047 9.03367C14.9916 8.6418 14.8713 8.19836 14.8438 7.70336C14.8301 7.35961 14.8232 6.91274 14.8232 6.36274C14.8232 5.81274 14.8301 5.37961 14.8438 5.06336C14.8713 4.56836 14.9916 4.12492 15.2047 3.73305C15.3283 3.50591 15.4789 3.30707 15.6567 3.13652L15.6568 3.1365C15.7857 3.01281 15.929 2.90401 16.0865 2.81008C16.0993 2.80241 16.1123 2.79487 16.1253 2.78747L16.1253 2.78745C16.4913 2.5791 16.9167 2.47492 17.4013 2.47492C17.8591 2.47492 18.2654 2.57047 18.6203 2.76155L18.6203 2.76159L18.6208 2.76184C18.6495 2.77729 18.6778 2.79337 18.7058 2.81008C18.8633 2.90396 19.0064 3.01272 19.1354 3.13634L19.1356 3.13652C19.3134 3.30707 19.464 3.50591 19.5876 3.73305C19.8007 4.12492 19.9244 4.56836 19.9588 5.06336ZM3.23401 4.1251C3.23401 3.9876 3.28901 3.88791 3.39901 3.82604L5.39963 2.70198C5.41304 2.69373 5.42676 2.68609 5.44078 2.67908C5.52026 2.63934 5.60967 2.61948 5.70901 2.61948L6.46182 2.61948C6.53745 2.61948 6.5976 2.64182 6.64229 2.68651C6.65156 2.69578 6.65987 2.70572 6.66722 2.71633L6.66728 2.7164C6.69531 2.75689 6.70932 2.80708 6.70932 2.86698L6.70932 9.92073C6.70932 9.99635 6.68698 10.0565 6.64229 10.1012C6.5976 10.1459 6.53745 10.1682 6.46182 10.1682L5.44088 10.1682C5.36526 10.1682 5.3051 10.1459 5.26042 10.1012C5.21573 10.0565 5.19338 9.99635 5.19338 9.92073L5.19338 4.26948L3.52276 5.1976C3.51245 5.20585 3.50152 5.21286 3.48997 5.21864C3.46302 5.23211 3.4327 5.23885 3.39901 5.23885C3.36096 5.23885 3.32948 5.2298 3.30459 5.2117C3.25754 5.17748 3.23401 5.1109 3.23401 5.01198L3.23401 4.1251ZM12.4615 7.56923C12.4684 7.4386 12.4718 7.04329 12.4718 6.38329C12.4718 5.71641 12.4684 5.3211 12.4615 5.19735C12.4409 4.76423 12.3378 4.43079 12.1522 4.19704C12.0681 4.09122 11.9714 4.00935 11.862 3.95144C11.7298 3.88142 11.579 3.84641 11.4097 3.84641C11.225 3.84641 11.0632 3.88626 10.9243 3.96594L10.9243 3.96595C10.8252 4.02274 10.7378 4.09977 10.662 4.19704C10.4798 4.43079 10.3784 4.76423 10.3578 5.19735C10.3509 5.3211 10.3475 5.71641 10.3475 6.38329C10.3475 7.04329 10.3509 7.4386 10.3578 7.56923C10.3784 8.00923 10.4798 8.3461 10.662 8.57985C10.7378 8.67709 10.8252 8.7541 10.9242 8.8109L10.9243 8.81094C11.0632 8.89063 11.225 8.93048 11.4097 8.93048C11.579 8.93048 11.7298 8.89547 11.862 8.82545L11.862 8.82545C11.9714 8.76753 12.0681 8.68567 12.1522 8.57985C12.3378 8.3461 12.4409 8.00923 12.4615 7.56923ZM18.4635 6.38329C18.4635 7.04329 18.4601 7.4386 18.4532 7.56923C18.4326 8.00923 18.3295 8.3461 18.1439 8.57985C18.0598 8.68567 17.9631 8.76754 17.8537 8.82545C17.7215 8.89547 17.5707 8.93048 17.4014 8.93048C17.2167 8.93048 17.0549 8.89063 16.916 8.81094C16.8169 8.75414 16.7295 8.67712 16.6537 8.57985C16.4715 8.3461 16.3701 8.00923 16.3495 7.56923C16.3426 7.4386 16.3392 7.04329 16.3392 6.38329C16.3392 5.71641 16.3426 5.3211 16.3495 5.19735C16.3701 4.76423 16.4715 4.43079 16.6537 4.19704C16.7295 4.09977 16.8169 4.02274 16.916 3.96595C17.0549 3.88626 17.2167 3.84641 17.4014 3.84641C17.5707 3.84641 17.7215 3.88142 17.8537 3.95144C17.9631 4.00935 18.0598 4.09122 18.1439 4.19704C18.3295 4.43079 18.4326 4.76423 18.4532 5.19735C18.4601 5.3211 18.4635 5.71641 18.4635 6.38329ZM25.003 4.5C24.5888 4.5 24.253 4.83579 24.253 5.25L24.253 7.75C24.253 8.16421 24.5888 8.5 25.003 8.5C25.4172 8.5 25.753 8.16421 25.753 7.75L25.753 5.25C25.753 4.83579 25.4172 4.5 25.003 4.5Z",
			fill: "currentColor",
			fillOpacity: "0.898",
			fillRule: "evenodd"
		})
	});
}
//#endregion
//#region src/components/Publis/StatusBar/icons/DualCardIcon.tsx
var Xc = ["ON", "OFF"];
function Zc({ G: e = "OFF", ...t }) {
	return /* @__PURE__ */ m("svg", {
		width: 18,
		height: 12,
		viewBox: "0 0 17.5 12.0003",
		fill: "none",
		"aria-hidden": "true",
		...t,
		children: /* @__PURE__ */ m("path", {
			d: "M16.5 0.000244141C15.9477 0.000244141 15.5 0.447959 15.5 1.00024L15.5 11.0002C15.5 11.5525 15.9477 12.0002 16.5 12.0002C17.0523 12.0002 17.5 11.5525 17.5 11.0002L17.5 1.00024C17.5 0.447959 17.0523 0.000244141 16.5 0.000244141ZM12.25 4.00024C12.25 3.44796 12.6977 3.00024 13.25 3.00024C13.8023 3.00024 14.25 3.44796 14.25 4.00024L14.25 11.0002C14.25 11.5525 13.8023 12.0002 13.25 12.0002C12.6977 12.0002 12.25 11.5525 12.25 11.0002L12.25 4.00024ZM10 5.50024C9.44772 5.50024 9 5.94796 9 6.50024L9 11.0002C9 11.5525 9.44772 12.0002 10 12.0002C10.5523 12.0002 11 11.5525 11 11.0002L11 6.50024C11 5.94796 10.5523 5.50024 10 5.50024ZM5.75 8.00024C5.75 7.44796 6.19772 7.00024 6.75 7.00024C7.30228 7.00024 7.75 7.44796 7.75 8.00024L7.75 11.0002C7.75 11.5525 7.30228 12.0002 6.75 12.0002C6.19772 12.0002 5.75 11.5525 5.75 11.0002L5.75 8.00024ZM3.5 8.25024C2.94772 8.25024 2.5 8.69796 2.5 9.25024L2.5 11.0002C2.5 11.5525 2.94772 12.0002 3.5 12.0002C4.05228 12.0002 4.5 11.5525 4.5 11.0002L4.5 9.25024C4.5 8.69796 4.05228 8.25024 3.5 8.25024Z",
			fill: "currentColor",
			fillOpacity: "0.898",
			fillRule: "evenodd"
		})
	});
}
//#endregion
//#region src/components/Publis/StatusBar/icons/SingleCardIcon.tsx
var Qc = ["ON", "OFF"];
function $c({ G: e = "OFF", ...t }) {
	return /* @__PURE__ */ h("svg", {
		width: 22,
		height: 12,
		viewBox: "0 0 21.5 12.0005",
		fill: "none",
		"aria-hidden": "true",
		...t,
		children: [/* @__PURE__ */ m("path", {
			d: "M1.75 8.00049C1.5865 8.00049 1.48825 8.05899 1.3515 8.20174C1.35045 8.2008 0.0665 9.63049 0.0665 9.63049C0.0655 9.63124 0.064 9.63174 0.063 9.63324C-0.021 9.71724 -0.021 9.85349 0.063 9.93749C0.10525 9.97949 0.16025 10.0005 0.21525 10.0005L1.25 10.0005L1.25 11.5005C1.25 11.7767 1.474 12.0005 1.75 12.0005C2.026 12.0005 2.25 11.7767 2.25 11.5005L2.25 8.50049C2.25 8.22449 2.026 8.00049 1.75 8.00049ZM5.1835 10.3705C5.1835 10.3705 3.89955 11.8007 3.8985 11.7997C3.76175 11.942 3.6635 12.0005 3.5 12.0005C3.224 12.0005 3 11.7767 3 11.5005L3 8.50049C3 8.22449 3.224 8.00049 3.5 8.00049C3.776 8.00049 4 8.22449 4 8.50049L4 10.0005L5.03475 10.0005C5.08975 10.0005 5.14475 10.0215 5.187 10.0635C5.271 10.148 5.271 10.2842 5.187 10.3677C5.186 10.3692 5.1845 10.3697 5.1835 10.3705Z",
			fill: "currentColor",
			fillOpacity: "0.898",
			fillRule: "evenodd"
		}), /* @__PURE__ */ m("path", {
			d: "M20.5 0.000488281C19.9477 0.000488281 19.5 0.448203 19.5 1.00049L19.5 11.0005C19.5 11.5528 19.9477 12.0005 20.5 12.0005C21.0523 12.0005 21.5 11.5528 21.5 11.0005L21.5 1.00049C21.5 0.448204 21.0523 0.000488281 20.5 0.000488281ZM16.25 4.00049C16.25 3.4482 16.6977 3.00049 17.25 3.00049C17.8023 3.00049 18.25 3.4482 18.25 4.00049L18.25 11.0005C18.25 11.5528 17.8023 12.0005 17.25 12.0005C16.6977 12.0005 16.25 11.5528 16.25 11.0005L16.25 4.00049ZM14 5.50049C13.4477 5.50049 13 5.9482 13 6.50049L13 11.0005C13 11.5528 13.4477 12.0005 14 12.0005C14.5523 12.0005 15 11.5528 15 11.0005L15 6.50049C15 5.9482 14.5523 5.50049 14 5.50049ZM9.75 8.00049C9.75 7.4482 10.1977 7.00049 10.75 7.00049C11.3023 7.00049 11.75 7.4482 11.75 8.00049L11.75 11.0005C11.75 11.5528 11.3023 12.0005 10.75 12.0005C10.1977 12.0005 9.75 11.5528 9.75 11.0005L9.75 8.00049ZM7.5 8.25049C6.94772 8.25049 6.5 8.6982 6.5 9.25049L6.5 11.0005C6.5 11.5528 6.94772 12.0005 7.5 12.0005C8.05228 12.0005 8.5 11.5528 8.5 11.0005L8.5 9.25049C8.5 8.6982 8.05228 8.25049 7.5 8.25049Z",
			fill: "currentColor",
			fillOpacity: "0.898",
			fillRule: "evenodd"
		})]
	});
}
//#endregion
//#region src/components/Publis/StatusBar/icons/WifiIcon.tsx
function el({ Flux: e = !1, style: t, ...n }) {
	return /* @__PURE__ */ m(Z, {
		"data-flux": e || void 0,
		name: "wifi",
		size: 16,
		style: {
			width: "15.3442px",
			height: "12px",
			...t
		},
		...n
	});
}
//#endregion
//#region src/components/Publis/StatusBar/StatusBar.tsx
var tl = ["Light", "Dark"], nl = [
	"1",
	"2",
	"3"
];
function rl({ "Color Mode": e = "Light", 类型: t = "1", dualCard5G: n = !1, Flux: r = !1, singleCard5G: i = !1, className: a, ...o }) {
	return /* @__PURE__ */ h("div", {
		className: X("hm-status-bar", e === "Dark" ? "hm-status-bar--dark" : "hm-status-bar--light", Q("StatusBar", { "Color Mode": e }), a),
		"data-color-mode": e,
		...o,
		children: [/* @__PURE__ */ m("span", {
			className: "hm-status-bar__time",
			children: "08:08"
		}), /* @__PURE__ */ h("div", {
			className: "hm-status-bar__icons",
			children: [
				/* @__PURE__ */ m(el, {
					Flux: r,
					className: "hm-status-bar__icon hm-status-bar__icon--wifi"
				}),
				/* @__PURE__ */ m($c, {
					G: i ? "ON" : "OFF",
					className: "hm-status-bar__icon hm-status-bar__icon--single-card"
				}),
				/* @__PURE__ */ m(Zc, {
					G: n ? "ON" : "OFF",
					className: "hm-status-bar__icon hm-status-bar__icon--dual-card"
				}),
				/* @__PURE__ */ m(Yc, {
					类型: t,
					className: "hm-status-bar__icon hm-status-bar__icon--cell"
				})
			]
		})]
	});
}
//#endregion
//#region src/components/Publis/StatusBar/index.ts
var il = /* @__PURE__ */ _({
	CellSignalIcon: () => Yc,
	DualCardIcon: () => Zc,
	SingleCardIcon: () => $c,
	StatusBar: () => rl,
	WifiIcon: () => el,
	cellSignalTypes: () => nl,
	cellTypes: () => Jc,
	colorModes: () => tl,
	dualCardGOptions: () => Xc,
	singleCardGOptions: () => Qc
}), al = [
	"Big",
	"Normal",
	"Secondary",
	"Drawer"
], ol = [
	"标准",
	"强",
	"降档",
	"弱"
], sl = [
	1,
	2,
	3
], cl = {
	Big: 3,
	Normal: 3,
	Secondary: 1,
	Drawer: 1
};
function ll({ buttonProps: e, disabled: t, icon: n, label: r, onClick: i, type: a = "button" }) {
	return /* @__PURE__ */ m("button", {
		"aria-label": r,
		className: "hm-floating-title-bar__icon-button",
		disabled: t,
		onClick: i,
		title: r,
		type: a,
		...e,
		children: /* @__PURE__ */ m("span", {
			"aria-hidden": "true",
			className: "hm-floating-title-bar__icon-glyph",
			children: n ?? /* @__PURE__ */ m(Z, {
				name: "circle_dashed",
				size: 20
			})
		})
	});
}
function ul({ kind: e = "back", icon: t, label: n, ...r }) {
	let i = m(e === "drawer" ? qc : Gc, { strokeWidth: 2.25 });
	return /* @__PURE__ */ m(ll, {
		...r,
		icon: t ?? i,
		label: n
	});
}
function dl(e) {
	return Array.from({ length: e }, (e, t) => ({
		id: `preview-${t + 1}`,
		label: `Action ${t + 1}`
	}));
}
function fl({ leadingAction: e, type: t }) {
	if (e !== null) {
		if (e) return e;
		if (t === "Secondary") return {
			kind: "back",
			label: "Back"
		};
		if (t === "Drawer") return {
			kind: "drawer",
			label: "Drawer"
		};
	}
}
function pl({ actions: e, iconCount: t }) {
	return e ? e.slice(0, t) : dl(t);
}
function ml({ 标题类型: e = "Big", 通透度: t = "标准", Icon: n, Size: r, title: i = "Title", subtitleText: a = "Subtitle", subtitle: o, leadingAction: s, actions: c, "Color Mode": l = "Light", 类型: u = "1", dualCard5G: d = !1, Flux: f = !1, singleCard5G: g = !1, iconButton尺寸: _ = 40, 属性1: v = "light", className: y, ...b }) {
	let x = n ?? cl[e], S = pl({
		actions: c,
		iconCount: x
	}), C = fl({
		leadingAction: s,
		type: e
	}), w = o ?? (r === "big title+subtitle" ? !0 : r === "Big title" ? !1 : void 0) ?? (e === "Big" || e === "Secondary");
	return /* @__PURE__ */ h("header", {
		className: X("hm-floating-title-bar", y),
		"data-icon": x,
		"data-icon-button-size": _,
		"data-mask": v,
		"data-title-type": e,
		"data-transparency": t,
		...b,
		children: [
			/* @__PURE__ */ m("div", { className: "hm-floating-title-bar__surface" }),
			/* @__PURE__ */ m(rl, {
				"Color Mode": l,
				类型: u,
				dualCard5G: d,
				Flux: f,
				singleCard5G: g,
				className: "hm-floating-title-bar__status"
			}),
			/* @__PURE__ */ m("div", {
				className: "hm-floating-title-bar__content",
				children: e === "Big" ? /* @__PURE__ */ h(p, { children: [/* @__PURE__ */ m("div", {
					className: "hm-floating-title-bar__actions hm-floating-title-bar__actions--top",
					children: S.map((e) => /* @__PURE__ */ m(ll, { ...e }, e.id ?? e.label))
				}), /* @__PURE__ */ h("div", {
					className: "hm-floating-title-bar__large-title",
					children: [/* @__PURE__ */ m("h1", {
						className: "hm-floating-title-bar__title hm-floating-title-bar__title--large",
						children: i
					}), w ? /* @__PURE__ */ m("p", {
						className: "hm-floating-title-bar__subtitle",
						children: a
					}) : null]
				})] }) : /* @__PURE__ */ h("div", {
					className: "hm-floating-title-bar__row",
					children: [/* @__PURE__ */ h("div", {
						className: "hm-floating-title-bar__left",
						children: [C ? /* @__PURE__ */ m(ul, { ...C }) : null, /* @__PURE__ */ h("div", {
							className: "hm-floating-title-bar__text",
							children: [/* @__PURE__ */ m("h1", {
								className: "hm-floating-title-bar__title",
								children: i
							}), w ? /* @__PURE__ */ m("p", {
								className: "hm-floating-title-bar__subtitle",
								children: a
							}) : null]
						})]
					}), /* @__PURE__ */ m("div", {
						className: "hm-floating-title-bar__actions",
						children: S.map((e) => /* @__PURE__ */ m(ll, { ...e }, e.id ?? e.label))
					})]
				})
			})
		]
	});
}
//#endregion
//#region src/components/Navigation/FloatingTitleBar/index.ts
var hl = /* @__PURE__ */ _({
	FloatingTitleBar: () => ml,
	floatingTitleBarIconOptions: () => sl,
	floatingTitleBarTransparencies: () => ol,
	floatingTitleBarTypes: () => al
}), gl = [
	0,
	1,
	2,
	3,
	4
];
function _l({ title: e = !0, Description: t = !0, className: n, ...r }) {
	return /* @__PURE__ */ m("div", {
		"aria-label": "Loading progress",
		"aria-valuemax": gl.length,
		"aria-valuemin": 0,
		"aria-valuenow": 1,
		className: X("hm-loading-progress-bar", n),
		"data-description-visible": t,
		"data-title-visible": e,
		role: "progressbar",
		...r,
		children: gl.map((e) => /* @__PURE__ */ m("span", {
			"aria-hidden": "true",
			className: "hm-loading-progress-bar__segment",
			"data-active": e === 0
		}, e))
	});
}
//#endregion
//#region src/components/Navigation/LoadingProgressBar/index.ts
var vl = /* @__PURE__ */ _({
	LoadingProgressBar: () => _l,
	loadingProgressBarSegments: () => gl
}), yl = [
	"banner-2in1",
	"number-phone",
	"progress-banner-phone"
], bl = [
	"28",
	"32",
	"40"
], xl = [
	3,
	4,
	5,
	6
];
function Sl({ 尺寸: e = "32", banners: t = [], 活跃索引: n, onIndexChange: r, className: i, ...o }) {
	let [s, c] = d(0), l = n !== void 0, u = t.length, f = Number.parseInt(e, 10), p = l ? u === 0 ? 0 : Math.max(0, Math.min(n, u - 1)) : s, g = a((e) => {
		if (u === 0) return;
		let t = Math.max(0, Math.min(e, u - 1));
		l || c(t), r?.(t);
	}, [
		u,
		r,
		l
	]), _ = a(() => g(p - 1), [g, p]), v = a(() => g(p + 1), [g, p]);
	return u === 0 ? /* @__PURE__ */ m("div", {
		className: X("swiper-banner-2in1", i),
		"data-size": e,
		"data-variant": "banner-2in1",
		...o,
		children: /* @__PURE__ */ m("div", {
			className: "swiper-banner-2in1__track",
			children: /* @__PURE__ */ m("div", { className: "swiper-banner-2in1__banner swiper-banner-2in1__banner--empty" })
		})
	}) : /* @__PURE__ */ m("div", {
		className: X("swiper-banner-2in1", i),
		"data-size": e,
		"data-variant": "banner-2in1",
		...o,
		children: /* @__PURE__ */ m("div", {
			className: "swiper-banner-2in1__track",
			children: t.map((e, t) => {
				let n = t - p;
				return /* @__PURE__ */ m("div", {
					className: X("swiper-banner-2in1__slide", t === p && "swiper-banner-2in1__slide--active"),
					style: { transform: `translateX(${n * 100}%)` },
					"aria-hidden": t !== p,
					children: /* @__PURE__ */ h("div", {
						className: "swiper-banner-2in1__banner",
						children: [
							/* @__PURE__ */ m("div", {
								className: "swiper-banner-2in1__banner-content",
								children: e
							}),
							/* @__PURE__ */ m("button", {
								type: "button",
								className: "swiper-banner-2in1__arrow swiper-banner-2in1__arrow--left",
								style: {
									width: f,
									height: f
								},
								onClick: (e) => {
									e.stopPropagation(), _();
								},
								"aria-label": "Previous",
								children: /* @__PURE__ */ m(Z, {
									className: "swiper-banner-2in1__chevron",
									name: "chevron_left",
									size: 24
								})
							}),
							/* @__PURE__ */ m("button", {
								type: "button",
								className: "swiper-banner-2in1__arrow swiper-banner-2in1__arrow--right",
								style: {
									width: f,
									height: f
								},
								onClick: (e) => {
									e.stopPropagation(), v();
								},
								"aria-label": "Next",
								children: /* @__PURE__ */ m(Z, {
									className: "swiper-banner-2in1__chevron",
									name: "chevron_right",
									size: 24
								})
							})
						]
					})
				}, `banner-${t}`);
			})
		})
	});
}
function Cl({ 当前页: e = 12, 总页数: t = 22, className: n, ...r }) {
	return /* @__PURE__ */ m("div", {
		className: X("hm-swiper-number-phone", n),
		"data-current": e,
		"data-total": t,
		"data-variant": "number-phone",
		...r,
		children: /* @__PURE__ */ h("span", {
			className: "hm-swiper-number-phone__text",
			children: [
				e,
				"/",
				t
			]
		})
	});
}
function wl({ 激活索引: e = 0, 进度数: t = 5, className: n, ...r }) {
	let i = Array.from({ length: t }, (e, t) => t);
	return /* @__PURE__ */ m("div", {
		className: X("hm-swiper-progress-banner-phone", n),
		"data-variant": "progress-banner-phone",
		...r,
		children: i.map((t) => /* @__PURE__ */ m("span", { className: X("hm-swiper-progress-banner-phone__segment", t === e && "hm-swiper-progress-banner-phone__segment--active") }, t))
	});
}
function Tl(e) {
	let { 变体: t, className: n, ...r } = e;
	switch (t) {
		case "banner-2in1": return /* @__PURE__ */ m(Sl, {
			className: n,
			...r
		});
		case "number-phone": return /* @__PURE__ */ m(Cl, {
			className: n,
			...r
		});
		case "progress-banner-phone": return /* @__PURE__ */ m(wl, {
			className: n,
			...r
		});
		default: return t;
	}
}
//#endregion
//#region src/components/Navigation/Swiper/index.ts
var El = /* @__PURE__ */ _({
	Swiper: () => Tl,
	iconSizes: () => bl,
	progressCounts: () => xl,
	swiperVariants: () => yl
}), Dl = [
	"OFF",
	"ON",
	"带symbol"
], Ol = [
	2,
	3,
	4,
	5,
	6
], kl = [
	"small",
	"medium",
	"large",
	"active",
	"large",
	"medium",
	"small"
];
function Al(e, t) {
	return Math.max(0, Math.min(e, Math.max(t - 1, 0)));
}
function jl(e, t) {
	if (e === t) return "active";
	let n = Math.abs(e - t);
	return n === 1 ? "large" : n === 2 ? "medium" : "small";
}
function Ml(e, t, n) {
	return e === "ON" ? Array.from({ length: kl.length }, (e, t) => jl(t, n)) : Array.from({ length: t }, (e, t) => t === n ? "active" : "large");
}
function Nl({ "Multi Dot": e = "OFF", 组数: t = 5, 活跃索引: n, onIndexChange: r, className: i, ...o }) {
	let s = e === "ON" ? kl.length : t, c = Math.floor(e === "ON" ? kl.length / 2 : t / 2), l = n !== void 0, [u, f] = d(c), p = Al(l ? n : u, s), g = a((e) => {
		l || f(e), r?.(e);
	}, [l, r]), _ = Ml(e, t, p);
	return /* @__PURE__ */ h("div", {
		className: X("swiper-dot", i),
		"data-type": e,
		"data-count": s,
		"data-active-index": p,
		role: "tablist",
		...o,
		children: [/* @__PURE__ */ m("div", {
			className: "swiper-dot__dots",
			children: _.map((t, n) => /* @__PURE__ */ m("button", {
				type: "button",
				className: X("swiper-dot__indicator-btn", "swiper-dot__indicator", `swiper-dot__indicator--${t}`),
				"aria-label": `第 ${n + 1} 页`,
				"aria-current": n === p ? "true" : void 0,
				onClick: () => g(n)
			}, `${e}-${n}`))
		}), e === "带symbol" ? /* @__PURE__ */ m("span", {
			className: "swiper-dot__symbol",
			children: "󰘗"
		}) : null]
	});
}
//#endregion
//#region src/components/Navigation/SwiperDot/index.ts
var Pl = /* @__PURE__ */ _({
	SwiperDot: () => Nl,
	swiperDotCounts: () => Ol,
	swiperDotTypes: () => Dl
}), Fl = [
	"normal-phone",
	"secondary page-phone",
	"title with icons-phone",
	"drawer-phone"
], Il = [
	1,
	2,
	3
], Ll = [
	"默认",
	"材质-标准",
	"材质-强",
	"材质-降档",
	"材质-弱"
], Rl = hs("w-[328px] max-w-full text-[color:var(--harmony-font-primary)]", {
	variants: { category: {
		"normal-phone": "flex min-h-14 items-center gap-2",
		"secondary page-phone": "flex min-h-14 items-center gap-2",
		"drawer-phone": "flex min-h-14 items-center gap-2",
		"title with icons-phone": "flex min-h-[137px] items-center gap-2"
	} },
	defaultVariants: { category: "normal-phone" }
}), zl = hs("inline-flex size-10 shrink-0 items-center justify-center rounded-full bg-[color:var(--harmony-comp-background-tertiary)] text-[color:var(--harmony-icon-primary)] outline-none transition-colors hover:bg-[color:var(--harmony-interactive-hover)] focus-visible:ring-2 focus-visible:ring-[color:var(--harmony-interactive-focus)] disabled:pointer-events-none disabled:opacity-40"), Bl = {
	1: "h1",
	2: "h2",
	3: "h3",
	4: "h4",
	5: "h5",
	6: "h6"
};
function Vl({ buttonProps: e, className: t, disabled: n, icon: r, label: i, onClick: a, type: o = "button" }) {
	return /* @__PURE__ */ m("button", {
		"aria-label": i,
		className: X(zl(), t),
		disabled: n,
		onClick: a,
		title: i,
		type: o,
		...e,
		children: /* @__PURE__ */ m("span", {
			"aria-hidden": "true",
			className: "inline-flex size-6 items-center justify-center [&_svg]:size-6 [&_svg]:shrink-0",
			children: r
		})
	});
}
function Hl({ kind: e = "back", icon: t, label: n, ...r }) {
	let i = m(e === "drawer" ? qc : Gc, { strokeWidth: 2.25 });
	return /* @__PURE__ */ m(Vl, {
		...r,
		className: "shrink-0",
		icon: t ?? i,
		label: n
	});
}
function Ul({ category: e, headingLevel: t, subtitle: n, subtitleText: r, title: i }) {
	let a = Bl[t], o = e === "title with icons-phone", s = o ? "text-[30px] leading-10" : n ? "text-[20px] leading-7" : "text-[26px] leading-[35px]", c = n ? /* @__PURE__ */ m("p", {
		className: "truncate text-[14px] leading-[19px] tracking-[0px] text-[color:var(--harmony-font-secondary)]",
		children: r
	}) : null, l = /* @__PURE__ */ m(a, {
		className: X("truncate font-bold tracking-[0px] text-[color:var(--harmony-font-primary)]", s),
		children: i
	});
	return /* @__PURE__ */ m("div", {
		className: X("min-w-0 flex-1", o && "flex flex-col gap-[2px]"),
		children: o ? /* @__PURE__ */ h(p, { children: [c, l] }) : /* @__PURE__ */ h(p, { children: [l, c] })
	});
}
function Wl(e) {
	return Array.from({ length: e }, (e, t) => ({
		id: `preview-${t + 1}`,
		icon: /* @__PURE__ */ m(Kc, { strokeWidth: 1.75 }),
		label: `Action ${t + 1}`
	}));
}
function Gl({ category: e, leadingAction: t, leftIcon: n }) {
	if (t !== null) {
		if (t) return t;
		if (e === "secondary page-phone") return n === !1 ? void 0 : {
			kind: "back",
			label: "Back"
		};
		if (e === "drawer-phone") return n === !1 ? void 0 : {
			kind: "drawer",
			label: "Drawer"
		};
	}
}
function Kl({ actions: e, Icon: t, rightIcon: n }) {
	return e ? e.slice(0, 3) : n === !1 || t === void 0 ? [] : Wl(t);
}
function ql({ actions: e, category: t = "normal-phone", headingLevel: n = 1, Icon: r, 通透度: i, leadingAction: a, leftIcon: o, rightIcon: s, subtitle: c = !1, subtitleText: l = "Subtitle", title: u = "Title", titleLeftSize: d }) {
	let f = c;
	return {
		actions: Kl({
			actions: e,
			Icon: r,
			rightIcon: s
		}),
		category: t,
		headingLevel: n,
		通透度: i,
		leadingAction: Gl({
			category: t,
			leadingAction: a,
			leftIcon: o
		}),
		subtitle: f,
		subtitleText: l,
		title: u,
		titleLeftSize: d
	};
}
function Jl({ actions: e, category: t = "normal-phone", className: n, headingLevel: r, Icon: i, 通透度: a, leadingAction: o, leftIcon: s, rightIcon: c, subtitle: l, subtitleText: u, title: d, titleLeftSize: f, ...p }) {
	let g = ql({
		actions: e,
		category: t,
		headingLevel: r,
		Icon: i,
		通透度: a,
		leadingAction: o,
		leftIcon: s,
		rightIcon: c,
		subtitle: l,
		subtitleText: u,
		title: d,
		titleLeftSize: f
	}), _ = g.actions.map((e) => /* @__PURE__ */ m(Vl, { ...e }, e.id ?? e.label));
	return g.category === "title with icons-phone" ? /* @__PURE__ */ h("header", {
		className: X(Rl({ category: g.category }), n),
		"data-category": g.category,
		"data-通透度": g.通透度,
		"data-title-left-size": g.titleLeftSize,
		"data-subtitle": g.subtitle,
		...p,
		children: [/* @__PURE__ */ m(Ul, {
			category: g.category,
			headingLevel: g.headingLevel,
			subtitle: g.subtitle,
			subtitleText: g.subtitleText,
			title: g.title
		}), _.length > 0 ? /* @__PURE__ */ m("div", {
			className: "flex shrink-0 items-center gap-2",
			children: _
		}) : null]
	}) : /* @__PURE__ */ h("header", {
		className: X(Rl({ category: g.category }), n),
		"data-category": g.category,
		"data-通透度": g.通透度,
		"data-subtitle": g.subtitle,
		...p,
		children: [/* @__PURE__ */ h("div", {
			className: "flex min-w-0 flex-1 items-center gap-2",
			children: [g.leadingAction ? /* @__PURE__ */ m(Hl, { ...g.leadingAction }) : null, /* @__PURE__ */ m(Ul, {
				category: g.category,
				headingLevel: g.headingLevel,
				subtitle: g.subtitle,
				subtitleText: g.subtitleText,
				title: g.title
			})]
		}), _.length > 0 ? /* @__PURE__ */ m("div", {
			className: "flex items-center gap-2",
			children: _
		}) : null]
	});
}
//#endregion
//#region src/components/Navigation/TitleBar/index.ts
var Yl = /* @__PURE__ */ _({
	TitleBar: () => Jl,
	titleBarCategories: () => Fl,
	titleBarIconOptions: () => Il,
	titleBar通透度Options: () => Ll
}), Xl = [
	"Light",
	"Dark",
	"Transparent"
];
function Zl({ "Color Mode": e = "Light", className: t, ...n }) {
	return /* @__PURE__ */ m("div", {
		className: X("hm-aibottombar", `hm-aibottombar--${e.toLowerCase()}`, Q("Aibottombar", { "Color Mode": e }), t),
		"data-color-mode": e,
		...n,
		children: /* @__PURE__ */ m("div", {
			className: "hm-aibottombar__pill",
			"aria-hidden": "true"
		})
	});
}
//#endregion
//#region src/components/Publis/Aibottombar/index.ts
var Ql = /* @__PURE__ */ _({
	Aibottombar: () => Zl,
	colorModes: () => Xl
}), $l = [
	"Text",
	"Text inline",
	"multiline text",
	"multiline text inline",
	"Full pattern",
	"Full pattern inline"
], eu = "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA", tu = "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA", nu = "Title", ru = "Text button", iu = { fontFamily: "HarmonyHeiTi, HarmonyHeiTi-Regular, var(--font-sans)" }, au = { fontFamily: "HarmonyHeiTi, HarmonyHeiTi-Medium, var(--font-sans)" };
function ou({ className: e, ...t }) {
	return /* @__PURE__ */ m(Z, {
		...t,
		className: X("size-[18px] shrink-0 cursor-pointer", e),
		name: "xmark",
		size: 18
	});
}
function su({ children: e, className: t }) {
	return /* @__PURE__ */ m("p", {
		className: X("w-[75px] h-5 shrink-0", "text-[14px] font-medium leading-[20px]", "text-[var(--harmony-font-emphasize)]", "truncate", t),
		style: au,
		children: e
	});
}
function cu() {
	return /* @__PURE__ */ m("div", {
		"aria-hidden": "true",
		className: "absolute left-6 top-[-6px] z-[1] h-3 w-3 rotate-45 rounded-[2px]",
		style: { background: "var(--COMPONENT_ULTRA_THICK_fill)" }
	});
}
function lu({ 类型: e = "Text", close: t = !0, image: n = !0, Link: r = !0, title: i, description: a, linkText1: o = ru, linkText2: s = ru, imageSrc: c, onClose: l, 方向: u = "Up", 箭头: d = "1", showArrow: f = !0, className: p, style: g, ..._ }) {
	let v = e.includes("inline"), y = e.startsWith("Text"), b = e.startsWith("multiline"), x = e.startsWith("Full pattern"), S = (y ? 10 : 12) == 10 ? "gap-2.5" : "gap-3", C = i ?? (x ? nu : eu), w = a ?? tu, T = c ?? "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAqgAAAKoCAIAAAA02poLAAAAAXNSR0IArs4c6QAAAERlWElmTU0AKgAAAAgAAYdpAAQAAAABAAAAGgAAAAAAA6ABAAMAAAABAAEAAKACAAQAAAABAAACqKADAAQAAAABAAACqAAAAAA5kNdeAABAAElEQVR4Ae3dBYBUVdvAcUW6QZBQupFeQmBhQVCRkO4OpaS7u3dZWlAEBQmlu2MBQaVBQlIQUEJCGkG/B3k/xM2Jc+7c+KMv7s7c+5zn/M6888zcOOell/iDAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIImFPgZXOmRVa6BW7dvqupiVQpkt+7d09TcDOHjRs37q+Xr2rKMFGCeJoiux5W1WvmyZMnASX8Dx8+5HrTbOmNQOLEiX/YszdFipTeBHm2rxleh973ggjRIEAAAQSMFHjllVcmTZkifxvZqJPbGjZ8hJKq72RDm/Wdwm+zAaU7CFhAIF++/O07dLRAotZPsWTJgAYNG1m/H/RApQCFX6UmsRBAwEWBnr16Z8qUycWN2cwzgThx4kyYNNmzfdnLxgIUfhsPLl1DwLwCsWPHlpr08stcZqRxjPr1H5AhQwaNDRDamgIUfmuOG1kjYH0Bf/8STZs1s34/TNqDAgUKtG7T1qTJkZZPBSj8PuWncQScLTBo8NBUqVI520BL76NHjz5x8pRo0XiH18Jr9aC8LKw+guSPgIUFEiZMGDR2nIU7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AAF1AhR+dZZEQgABBBBAwPQCFH7TDxEJIoAAAgggoE6Awq/OkkgIIIAAAgiYXoDCb/ohIkEEEEAAAQTUCVD41VkSCQEEEEAAAdMLUPhNP0QkiAACCCCAgDoBCr86SyIhgAACCCBgegEKv+mHiAQRQAABBBBQJ0DhV2dJJAQQQAABBEwvQOE3/RCRIAIIIIAAAuoEKPzqLImEAAIIIICA6QUo/KYfIhJEAAEEEEBAnQCFX50lkRBAAAEEEDC9AIXf9ENEgggggAACCKgToPCrsyQSAggggAACpheg8Jt+iEgQAQQQQAABdQIUfnWWREIAAQQQQMD0AhR+0w8RCSKAAAIIIKBOgMKvzpJICCCAAAIImF6Awm/6ISJBBBBAAAEE1AlQ+NVZEgkBBBBAAAHTC1D4TT9EJIgAAggggIA6AQq/OksiIYAAAgggYHoBCr/ph4gEEUAAAQQQUCdA4VdnSSQEEEAAAQRML0DhN/0QkSACCCCAAALqBCj86iyJhAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAqEEXg71O78iYGaBWLFiZcqUOUvWLFmyZE2ZKlWC+PInwf/+efrjPw/Ej//nn3/euXP79u078rf88/Tnf/66devW2bNnTp44efLkiV9//dXMPSU3gwVefvnluHHjxosnL6N48vezf+LEjfPnn48fPXz48On/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42XhOGMbpzU1AnJfSZEib8nrqnTpt/PkzSvL/6iJ63KUo0ePbJf78UO2frtjh0xw6fJ+bIiAXgEKv15forsrIHcBFPDzCwgoVTIgQN61jbxrS+Ye+KfSP633ly5dcjdztjezgHwIePPNN2VuiXz58svfWbJk1fH58tq1q6dPnT5yROp9yLbt21igwcwvCSfnRuF38uibve9yAaBM2JI9e3Z5m5a7AeVvOTWg6vTtnTt3TskVVidPyl+y0MCBA/tlnl2zi5CfOgGZBzBjpowZMmSUP6lSpUqWLPmrr8qNAsnkf4kSJQq3HTliLyfp796V185d+e/tP26fP3/utPw5dUr+J68fuUo/3B15EAFTCVD4TTUcJBOFgBwAyJQps3wMkA8BKVOlSiCLAsVP8L9/nv74zwPx48uJ+Tt35FyqvEHfln+e/ixv1XfuyPvymTOnT56Qcn+Ca/KjsHb203JeQF5scpwgZsxYMWJEv//ggRR8qfrOVqH3CCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIKBI4GVFcQhjZ4FXYr/6RtNrdu6h7/p29/iMa1ua+659WkYAAccJRHNcj+kwAggggAACDhag8Dt48Ok6AggggIDzBCj8zhtzeowAAggg4GABCr+DB5+uI4AAAgg4T4DC77wxp8cIIIAAAg4WoPA7ePDpOgIIIICA8wQo/M4bc3qMAAIIIOBgAQq/gwefriOAAAIIOE+Awu+8MafHCCCAAAIOFqDwO3jw6ToCCCCAgPMEKPzOG3N6jAACCCDgYAEKv4MHn64jgAACCDhPgMLvvDGnxwgggAACDhag8Dt48Ok6AggggIDzBCj8zhtzeowAAggg4GABCr+DB5+uI4AAAgg4T4DC77wxp8cIIIAAAg4WoPA7ePDpOgIIIICA8wQo/M4bc3qMAAIIIOBgAQq/gwefriOAAAIIOE+Awu+8MafHCCCAAAIOFqDwO3jw6ToCCCCAgPMEKPzOG3N6jAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACDhf4P2d81mxy6mkDAAAAAElFTkSuQmCC";
	return /* @__PURE__ */ m(ar, {
		方向: u,
		箭头: d,
		arrow: f && !v,
		glass: !v,
		className: X("hm-popup-tip !w-[312px] !h-auto !block", !v && "drop-shadow-[0_0_50px_rgba(0,0,0,0.15)]", p),
		style: {
			...v && { "--popup-surface-bg": "var(--harmony-comp-background-tertiary)" },
			...g
		},
		..._,
		children: /* @__PURE__ */ h("div", {
			className: X("relative z-[2] isolate overflow-hidden flex flex-row items-start", "w-full", S, "rounded-[20px]", "backdrop-blur-none", y && !v && "p-3", y && v && "py-2 px-4", !y && "p-3", y && "items-center"),
			children: [x && n && /* @__PURE__ */ m("div", {
				className: "size-8 shrink-0 rounded-lg bg-cover bg-center bg-no-repeat",
				style: { backgroundImage: `url(${T})` }
			}), /* @__PURE__ */ h("div", {
				className: X("flex flex-col items-start flex-1 min-w-0", !y && "gap-2", y && "gap-0"),
				children: [
					/* @__PURE__ */ h("div", {
						className: X("flex flex-row w-full", S, y ? "items-center" : "items-start"),
						children: [x ? /* @__PURE__ */ m("p", {
							className: X("text-[16px] font-medium leading-[22px]", "text-[var(--harmony-font-primary)]", "line-clamp-1 flex-1 min-w-0"),
							style: au,
							children: C
						}) : b ? /* @__PURE__ */ m("p", {
							className: X("text-[14px] font-normal leading-[19px]", "text-[var(--harmony-font-secondary)]", "line-clamp-2 h-[38px] flex-1 min-w-0 overflow-hidden text-ellipsis break-all whitespace-normal"),
							style: iu,
							children: w
						}) : /* @__PURE__ */ m("p", {
							className: X("text-[14px] font-normal leading-[20px]", "text-[var(--harmony-font-primary)]", "line-clamp-1 h-5 flex-1 min-w-0 overflow-hidden text-ellipsis whitespace-nowrap"),
							style: iu,
							children: C
						}), t && /* @__PURE__ */ m(ou, {
							className: X(y && "mt-0.5"),
							onClick: l
						})]
					}),
					x && /* @__PURE__ */ m("p", {
						className: X("text-[14px] font-normal leading-[19px]", "text-[var(--harmony-font-secondary)]", "line-clamp-2 h-[38px] w-full overflow-hidden text-ellipsis break-all whitespace-normal"),
						style: iu,
						children: w
					}),
					(b || x) && r && /* @__PURE__ */ h("div", {
						className: "flex flex-row items-center gap-4 w-full",
						children: [/* @__PURE__ */ m(su, { children: o }), /* @__PURE__ */ m(su, { children: s })]
					})
				]
			})]
		})
	});
}
//#endregion
//#region src/components/Views/PopupTip/index.ts
var uu = /* @__PURE__ */ _({
	CloseIcon: () => ou,
	PopupTip: () => lu,
	PopupTipArrow: () => cu,
	TextLink: () => su,
	popupTipTypes: () => $l
});
//#endregion
//#region src/components/Publis/Pattern/Pattern.tsx
function du({ items: e, className: t }) {
	return /* @__PURE__ */ m("div", {
		className: X("pattern__card-group", t),
		children: e.map((t, n) => /* @__PURE__ */ m(Rn, {
			行数: "1",
			title: t.title,
			subtitle: t.subtitle,
			right: t.right ? "Text" : "Arrow",
			rightText: t.right,
			divider: n < e.length - 1
		}, n))
	});
}
function fu({ cardGroups: e, subHeaders: t, footnote: n, titleBarTitle: r }) {
	return /* @__PURE__ */ h("div", {
		className: "pattern__phone flex flex-col items-center",
		children: [
			/* @__PURE__ */ m(rl, { "Color Mode": "Light" }),
			/* @__PURE__ */ m("div", {
				className: "w-[328px]",
				children: /* @__PURE__ */ m(Jl, {
					category: "secondary page-phone",
					title: r,
					leadingAction: {
						kind: "back",
						label: "返回"
					}
				})
			}),
			t.length > 0 && t[0].副标题 && /* @__PURE__ */ m("p", {
				className: "mt-[28px] w-[328px] pl-3 text-[14px] leading-[20px] text-[var(--harmony-font-secondary)]",
				children: t[0].副标题
			}),
			e.length > 0 && /* @__PURE__ */ m(du, {
				items: e[0].items,
				className: "mt-[8px]"
			}),
			e.length > 1 && /* @__PURE__ */ m(du, {
				items: e[1].items,
				className: "mt-3"
			}),
			/* @__PURE__ */ m("p", {
				className: "mt-2 w-[328px] pl-3 text-[12px] leading-[16px] text-[var(--harmony-font-tertiary)]",
				children: n
			}),
			e.length > 2 && /* @__PURE__ */ m(du, {
				items: e[2].items,
				className: "mt-4"
			}),
			t.length > 1 && t[1].副标题 && /* @__PURE__ */ m("p", {
				className: "mt-[28px] w-[328px] pl-3 text-[14px] leading-[20px] text-[var(--harmony-font-secondary)]",
				children: t[1].副标题
			}),
			e.length > 3 && /* @__PURE__ */ m(du, {
				items: e[3].items,
				className: "mt-[8px]"
			})
		]
	});
}
function pu({ cardGroups: e, subHeaders: t, titleBarTitle: n, description: r, footnote: i }) {
	return /* @__PURE__ */ h("div", {
		className: "pattern__phone flex flex-col items-center",
		children: [
			/* @__PURE__ */ m(rl, { "Color Mode": "Light" }),
			/* @__PURE__ */ m("div", {
				className: "w-[328px]",
				children: /* @__PURE__ */ m(Jl, {
					category: "secondary page-phone",
					title: n,
					leadingAction: {
						kind: "back",
						label: "返回"
					}
				})
			}),
			/* @__PURE__ */ m("div", {
				className: "mt-[16px] w-[328px] pl-3 flex justify-start",
				children: /* @__PURE__ */ m("p", {
					className: "pattern__text-description",
					children: r
				})
			}),
			t.length > 0 && t[0].副标题 && /* @__PURE__ */ m("p", {
				className: "mt-[28px] w-[328px] pl-3 text-[14px] leading-[20px] text-[var(--harmony-font-secondary)]",
				children: t[0].副标题
			}),
			e.length > 0 && /* @__PURE__ */ m(du, {
				items: e[0].items,
				className: "mt-[8px]"
			}),
			e.length > 1 && /* @__PURE__ */ m(du, {
				items: e[1].items,
				className: "mt-3"
			}),
			/* @__PURE__ */ m("p", {
				className: "mt-2 w-[328px] pl-3 text-[12px] leading-[16px] text-[var(--harmony-font-tertiary)]",
				children: i
			}),
			e.length > 2 && /* @__PURE__ */ m(du, {
				items: e[2].items,
				className: "mt-4"
			})
		]
	});
}
function mu({ cardGroups: e, subHeaders: t, titleBarTitle: n, popupTipDescription: r }) {
	return /* @__PURE__ */ h("div", {
		className: "pattern__phone flex flex-col items-center",
		children: [
			/* @__PURE__ */ m(rl, { "Color Mode": "Light" }),
			/* @__PURE__ */ m("div", {
				className: "w-[328px]",
				children: /* @__PURE__ */ m(Jl, {
					category: "secondary page-phone",
					title: n,
					leadingAction: {
						kind: "back",
						label: "返回"
					}
				})
			}),
			/* @__PURE__ */ m("div", {
				className: "mt-[8px]",
				children: /* @__PURE__ */ m(lu, {
					类型: $l[5],
					description: r
				})
			}),
			t.length > 0 && t[0].副标题 && /* @__PURE__ */ m("p", {
				className: "mt-[28px] w-[328px] pl-3 text-[14px] leading-[20px] text-[var(--harmony-font-secondary)]",
				children: t[0].副标题
			}),
			e.map((e, t) => /* @__PURE__ */ m(du, {
				items: e.items,
				className: t === 0 ? "mt-[8px]" : "mt-3"
			}, t)),
			/* @__PURE__ */ m("p", {
				className: "mt-2 w-[328px] pl-3 text-[12px] leading-[16px] text-[var(--harmony-font-tertiary)]",
				children: "退出账号后，部分功能将不可用"
			})
		]
	});
}
function hu({ cardGroups: e, titleBarTitle: t, illustrationTitle: n, illustrationDescription: r, illustrationSrc: i, illustrationChildren: a }) {
	return /* @__PURE__ */ h("div", {
		className: "pattern__phone flex flex-col items-center",
		children: [
			/* @__PURE__ */ m(rl, { "Color Mode": "Light" }),
			/* @__PURE__ */ m("div", {
				className: "w-[328px]",
				children: /* @__PURE__ */ m(Jl, {
					category: "secondary page-phone",
					title: t,
					Icon: 1,
					leadingAction: {
						kind: "back",
						label: "返回"
					}
				})
			}),
			/* @__PURE__ */ m("div", {
				className: "mt-[8px] size-[288px] overflow-hidden flex items-center justify-center",
				children: a || (i ? /* @__PURE__ */ m("img", {
					src: i,
					alt: n,
					className: "size-full object-cover"
				}) : /* @__PURE__ */ h("div", {
					className: "flex flex-col items-center gap-2 text-slate-400",
					children: [/* @__PURE__ */ m(Z, {
						name: "rectangle",
						size: 64,
						style: { transform: "rotate(90deg)" }
					}), /* @__PURE__ */ m("span", {
						className: "text-xs",
						children: "Illustration"
					})]
				}))
			}),
			/* @__PURE__ */ m("h2", {
				className: "mt-[24px] w-[312px] text-center text-[var(--harmony-font-size-title-s)] font-medium leading-[27px] text-[var(--harmony-font-primary)]",
				children: n
			}),
			/* @__PURE__ */ m("p", {
				className: "pattern__illustration-desc mt-[8px] pl-3",
				children: r
			}),
			/* @__PURE__ */ m(Nl, {
				className: "mt-[8px]",
				"Multi Dot": "OFF",
				组数: 3
			}),
			e.length > 0 && /* @__PURE__ */ m(du, {
				items: e[0].items,
				className: "mt-[8px]"
			}),
			/* @__PURE__ */ m("p", {
				className: "mt-2 w-[328px] pl-3 text-[12px] leading-[16px] text-[var(--harmony-font-tertiary)]",
				children: "了解更多关于设置信息"
			}),
			/* @__PURE__ */ m("div", {
				className: "absolute bottom-0 left-0 w-full",
				children: /* @__PURE__ */ m(Zl, { "Color Mode": "Light" })
			})
		]
	});
}
var gu = [
	{ items: [{ title: "账号与安全" }, { title: "隐私设置" }] },
	{ items: [{ title: "通知管理" }, { title: "通用设置" }] },
	{ items: [{ title: "主题与壁纸" }, { title: "字体与显示" }] },
	{ items: [{ title: "存储与数据" }, { title: "辅助功能" }] }
], _u = [{
	标题: "常用设置",
	副标题: "包含账户、隐私等基础管理功能"
}, {
	标题: "更多设置",
	副标题: "其他管理选项"
}], vu = [
	{ items: [{ title: "账号与安全" }, { title: "隐私设置" }] },
	{ items: [{ title: "通知管理" }, { title: "通用设置" }] },
	{ items: [{ title: "主题与壁纸" }, { title: "字体与显示" }] }
];
function yu({ 布局: e = "默认", titleBarTitle: t = "设置", cardGroups: n, subHeaders: r, footnote: i = "设置应用的各项参数，以上信息仅部分展示", description: a = "管理您的账户信息、隐私与安全设置，以及应用权限和应用通知偏好。所有个性化选项均集中于此页面中。", popupTipTitle: o = "新功能提示", popupTipDescription: s = "新的暗色模式已上线，前往设置主题与壁纸中体验更护眼的深色界面风格。", illustrationTitle: c = "个性化您的专属设置", illustrationDescription: l = "管理您的账户、隐私、通知和应用权限偏好", illustrationSrc: u = "", illustrationChildren: d, className: f, ...p }) {
	let g = {
		cardGroups: n ?? (e === "默认" ? gu : vu),
		subHeaders: r ?? (e === "默认" ? _u : [{
			标题: "常用设置",
			副标题: "包含账户、隐私等基础管理功能"
		}]),
		titleBarTitle: t,
		footnote: i ?? "设置应用的各项参数，以上信息仅部分展示",
		description: a,
		popupTipTitle: o,
		popupTipDescription: s,
		illustrationTitle: c,
		illustrationDescription: l,
		illustrationSrc: u || "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAkAAAAJACAYAAABlmtk2AACHVklEQVR4Ae3gAZAkSZIkSRKLqpm7R0REZmZmVlVVVVV3d3d3d/fMzMzMzMzMzMzMzMzMzMzMzMzMzMzMzMzMzMzMzMzMzMzMzMzMzMzMzMzMzMzMzMzMzMzMzMzMzMzMzMzMzMzMzMzMzMzMzMzMzMzMzMzMzMzMzMzMdHd3d3dXV1VVVVVmZkZGRIS7m5kKz0xmV3d1d3dPz8zMzMxMorjqqquuuuqqq676/wVx1VVXXXXVVVdd9f8L4qqrrrrqqquuuur/F8RVV1111VVXXXXV/y+Iq6666qqrrrrqqv9fEFddddVVV1111VX/vyCuuuqqq6666qqr/n9BXHXVVVddddVVV/3/grjqqquuuuqqq676/wVx1VVXXXXVVVdd9f8L4qqrrrrqqquuuur/F8RVV1111VVXXXXV/y+Iq6666qqrrrrqqv9fEFddddVVV1111VX/vyCuuuqqq6666qqr/n9BXHXVVVddddVVV/3/grjqqquuuuqqq676/wVx1VVXXXXVVVdd9f8L4qqrrrrqqquuuur/F8RVV1111VVXXXXV/y+Iq6666qqrrrrqqv9fEFddddVVV1111VX/vyCuuuqqq6666qqr/n9BXHXVVVddddVVV/3/grjqqquuuuqqq676/wVx1VVXXXXVVVdd9f8L4qqrrrrqqquuuur/F8RVV1111VVXXXXV/y+Iq6666qqrrrrqqv9fEFddddVVV1111VX/vyCuuuqqq6666qqr/n9BXHXVVVddddVVV/3/grjqqquuuuqqq676/wVx1VVXXXXVVVdd9f8L4qqrrrrqqquuuur/F8RVV1111VVXXXXV/y+Iq6666qqrrrrqqv9fEFddddVVV1111VX/vyCuuuqqq6666qqr/n9BXHXVVVddddVVV/3/grjqqquuuuqqq676/wVx1VVXXXXVVVdd9f8L4qqrrrrqqquuuur/F8RVV1111VVXXXXV/y+Iq6666qqrrrrqqv9fEFddddVVV1111VX/vyCuuuqqq6666qqr/n9BXHXVVVddddVVV/3/grjqqquuuuqqq676/wVx1VVXXXXVVVdd9f8L4qqrrrrqqquuuur/F8RVV1111VVXXXXV/y+Iq6666qqrrrrqqv9fEFddddVVV111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q676/w1x1VVXXfaWb/mW21G3vgr80lx11f85+uuujB/xYz/2Y0uuuuoqxFVXXfUs7/AO77AYW/1s4PW46qr/O36jK9Nn/9iP/diSq666CgBx1VVXPY+3ftt3fm/QhwCFq67636shvu6nf+KHvp+rrrrqgRBXXXXV8/U2b/NOj3TEZ2MeyVVX/W8jP17pz/upn/qRJ3HVVVc9N8RVV131Ar3DO7xDGbO+BfhDsE5x1VX/08nnQd/UxfRzP/ZjP9a46qqrnh/EVVdd9S96h3d4h37M+tbA22EexlVX/U8jngr8RBfTT//Yj/3YwFVXXfXCIK666qp/lbd+63d6GKHXAF4O6cUx21x11X81sY/998BfkP69n/7pH3kqV1111YsKcdVVV/27vO3bvvv1dnuwgxtwngLdAFqAjwMFcS0PZF3PVVc9N/luHsjcCzTQLngJvgvFeSV3SeXWn/zJ77+bq6666t8KcdVVV1111VVXXfX/C+Kqq6666qqrrrrq/xfEVVddddVVV1111f8viKuuuuqqq6666qr/XxBXXXXVVVddddVV/78grrrqqquuuuqqq/5/QVx11VVXXXXVVVf9/4K46qqrrrrqqquu+v8FcdVVV1111VVXXfX/C+Kqq6666qqrrrrq/xfEVVddddVVV1111f8viKuuuuqqq6666qr/XxBXXXXVVVddddVV/78grrrqqquuuuqqq/5/QVx11VVXXXXVVVf9/4K46qqrrrrqqquu+v8FcdVVV1111VVXXfX/C+Kqq6666qqrrrrq/xfEVVddddVVV1111f8viKuuuuqqq6666qr/XxBXXXXVVVddddVV/78grrrqqquuuuqqq/5/QVx11VVXXXXVVVf9/4K46qqrrrrqqquu+v8FcdVVV1111VVXXfX/C+Kqq6666qqrrrrq/xfEVVddddVVV1111f8viKuuuuqqq6666qr/XxBXXXXVVVddddVV/78grrrqqquuuuqqq/5/QVx11VVXXXXVVVf9/4K46qqrrrrqqquu+v8FcdVVV1111VVXXfX/C+Kqq6666qqrrrrq/xfEVVddddVVV1111f8viKuuuuqqq6666qr/XxBXXXXVVVddddVV/78grrrqqquuuuqqq/5/QVx11VVXXXXVVVf9/4K46qqrrrrqqquu+v8FcdVVV1111VVXXfX/C+Kqq6666qqrrrrq/xfEVVddddVVV1111f8viKuuuuqqq6666qr/XxBXXXXVVVddddVV/78grrrqqquuuuqqq/5/QVx11VVXXXXVVVf9/4K46qqrrrrqqquu+v8FcdVVV1111VVXXfX/C+Kqq6666qqrrrrq/xfEVVddddVVV1111f8viKuuuuqqq6666qr/XxBXXXXVVVddddVV/78grrrqqquuuuqqq/5/QVx11VVXXXXVVVf9/4K46qqrrrrqqquu+v8FcdVVV1111VVXXfX/C+Kqq6666qqrrrrq/xfEVVddddVVV1111f8viKuuuuqqq6666qr/XxBXXXXVVVddddVV/78grrrqqquuuuqqq/5/QVx11VVXXXXVVVf9/4K46qqrrrrqqquu+v8FcdVVV1111VVXXfX/C+Kqq6666qqrrrrq/xfEVVddddVVV1111f8viKuuuuqqq6666qr/XxBXXXXVVVddddVV/78grrrqqquuuuqqq/5/QVx11VVXXXXVVVf9/4K46qqrrrrqqquu+v8FcdVVV1111VVXXfX/C+Kqq6666qqrrrrq/xfEVVddddVVV1111f8viKuuuuqqq6666qr/XxBXXXXVVVddddVV/78grrrqqquuuuqqq/5/4R8B04dZMD0feMcAAAAASUVORK5CYII="
	};
	return /* @__PURE__ */ h("div", {
		className: X(f),
		...p,
		children: [
			e === "默认" && /* @__PURE__ */ m(fu, {
				...g,
				footnote: g.footnote
			}),
			e === "文本" && /* @__PURE__ */ m(pu, {
				...g,
				cardGroups: g.cardGroups.slice(0, 3)
			}),
			e === "卡片" && /* @__PURE__ */ m(mu, {
				...g,
				cardGroups: g.cardGroups.slice(0, 3)
			}),
			e === "插画" && /* @__PURE__ */ m(hu, {
				...g,
				cardGroups: g.cardGroups.slice(0, 1),
				illustrationChildren: d
			})
		]
	});
}
//#endregion
//#region src/components/Publis/Pattern/pattern.constants.ts
var bu = [
	"默认",
	"文本",
	"卡片",
	"插画"
], xu = /* @__PURE__ */ _({
	Pattern: () => yu,
	patternLayoutOptions: () => bu
}), Su = [
	"Phone",
	"Tablet",
	"Foldable"
], Cu = ["OFF", "ON"];
function wu(e, t) {
	let n = t === "ON";
	switch (e) {
		case "Phone": return X("hm-phone", n ? "hm-phone--landscape" : "hm-phone--portrait");
		case "Tablet": return X("hm-tablet", n ? "hm-tablet--landscape" : "hm-tablet--portrait");
		case "Foldable": return "hm-foldable";
	}
}
function Tu(e) {
	switch (e) {
		case "Phone": return "hm-phone__content";
		case "Tablet": return "hm-tablet__content";
		case "Foldable": return "hm-foldable__content";
	}
}
function Eu({ variant: e, Land: t = "OFF", className: n, ...r }) {
	return /* @__PURE__ */ h("div", {
		className: X(wu(e, t), n),
		"data-type": e,
		"data-land": e === "Foldable" ? void 0 : t,
		...r,
		children: [
			/* @__PURE__ */ m(rl, { "Color Mode": "Light" }),
			/* @__PURE__ */ m("div", { className: Tu(e) }),
			/* @__PURE__ */ m(Zl, { "Color Mode": "Light" })
		]
	});
}
function Du({ Land: e = "OFF", ...t }) {
	return /* @__PURE__ */ m(Eu, {
		variant: "Phone",
		Land: e,
		...t
	});
}
function Ou({ Land: e = "OFF", ...t }) {
	return /* @__PURE__ */ m(Eu, {
		variant: "Tablet",
		Land: e,
		...t
	});
}
function ku(e) {
	return /* @__PURE__ */ m(Eu, {
		variant: "Foldable",
		...e
	});
}
function Au({ 类型: e = "Phone", ...t }) {
	switch (e) {
		case "Tablet": return /* @__PURE__ */ m(Ou, { ...t });
		case "Foldable": return /* @__PURE__ */ m(ku, { ...t });
		default: return /* @__PURE__ */ m(Du, { ...t });
	}
}
//#endregion
//#region src/components/Publis/Size/index.ts
var ju = /* @__PURE__ */ _({
	Size: () => Au,
	SizeFoldable: () => ku,
	SizePhone: () => Du,
	SizeTablet: () => Ou,
	landOptions: () => Cu,
	sizeTypes: () => Su
}), Mu = ["OFF", "ON"], Nu = [
	"Default",
	"Hover",
	"Pressed",
	"Focus"
];
function Pu({ 选项: e, Hyperlink: t, 状态: n = "Default", 选中变更: r, 超链接点击: i, className: o }) {
	let s = t ?? (e.some((e) => e.超链接 !== void 0) ? "ON" : "OFF"), [c, u] = d(() => new Set(e.filter((e) => e.选中).map((e) => e.值))), f = l(() => {
		let t = new Set(c);
		for (let n of e) n.选中 !== void 0 && n.选中 && t.add(n.值);
		return t;
	}, [e, c]), p = a((e) => {
		if (e.禁用) return;
		let t = !f.has(e.值);
		u((n) => {
			let r = new Set(n);
			return t ? r.add(e.值) : r.delete(e.值), r;
		}), r?.(e, t);
	}, [r, f]), g = a((e, t) => {
		e.stopPropagation(), !t.禁用 && i?.(t);
	}, [i]), _ = {
		Default: "",
		Hover: "bg-[var(--harmony-comp-background-tertiary)]",
		Pressed: "bg-[var(--harmony-interactive-click)]",
		Focus: "ring-2 ring-[var(--harmony-brand)] ring-inset"
	}, v = n === "Default";
	return /* @__PURE__ */ m("div", {
		className: X("flex flex-col", o),
		role: "group",
		"aria-label": "复选框组",
		children: e.map((e) => {
			let t = s === "ON" && e.超链接 !== void 0, r = e.禁用;
			return /* @__PURE__ */ h("div", {
				className: X("flex flex-row items-center gap-3 py-3 px-0 rounded-lg select-none transition-colors min-h-[48px] w-[328px]", !t && _[n], !t && v && "hover:bg-[var(--harmony-comp-background-tertiary)] active:bg-[var(--harmony-interactive-click)]", r && "opacity-40 pointer-events-none"),
				role: "checkbox",
				"aria-checked": f.has(e.值),
				"aria-disabled": r,
				children: [/* @__PURE__ */ m(vn, {
					type: "phone",
					Selected: f.has(e.值) ? "ON" : "OFF",
					状态: r ? "Disabled" : "Enabled",
					onClick: () => p(e)
				}), /* @__PURE__ */ h("div", {
					className: "flex-1 flex flex-row items-center min-w-0 gap-0 cursor-pointer",
					onClick: () => p(e),
					tabIndex: r ? -1 : 0,
					onKeyDown: (t) => {
						(t.key === "Enter" || t.key === " ") && (t.preventDefault(), p(e));
					},
					children: [/* @__PURE__ */ m("span", {
						className: X("text-sm leading-[19px] truncate", "text-[var(--harmony-font-primary)]"),
						children: e.标签
					}), t && /* @__PURE__ */ m("button", {
						type: "button",
						className: X("flex-shrink-0 text-sm leading-[19px] rounded-[2px]", "text-[var(--harmony-font-emphasize)]", "focus:outline-none", n === "Hover" && "bg-[var(--harmony-comp-background-tertiary)]", n === "Pressed" && "bg-[var(--harmony-interactive-click)]", v && "hover:bg-[var(--harmony-comp-background-tertiary)] active:bg-[var(--harmony-interactive-click)]", n === "Focus" && "ring-2 ring-[var(--harmony-brand)] rounded-[3px] px-0.5 py-[1.5px]"),
						onClick: (t) => g(t, e),
						tabIndex: r ? -1 : 0,
						children: e.超链接
					})]
				})]
			}, e.值);
		})
	});
}
//#endregion
//#region src/components/Selection/CheckboxGroup/index.ts
var Fu = /* @__PURE__ */ _({
	CheckboxGroup: () => Pu,
	checkboxGroupHyperlinks: () => Mu,
	checkboxGroupStates: () => Nu
}), Iu = [
	"Mini",
	"Small",
	"Medium"
];
function Lu({ 类型: e = "Mini", selected: t = !1, children: n, className: r, ...i }) {
	let a = {
		Mini: 36,
		Small: 36,
		Medium: 56
	}[e];
	return /* @__PURE__ */ m("div", {
		className: X("picker-item", `picker-item--${e.toLowerCase()}`, t && "picker-item--selected", r),
		style: { height: a },
		"data-type": e,
		"data-selected": t,
		...i,
		children: /* @__PURE__ */ m("span", {
			className: "picker-item__text",
			children: n
		})
	});
}
//#endregion
//#region src/components/Selection/Picker/picker-column.tsx
var Ru = 72, zu = 180;
function Bu({ items: e, selectedIndex: t = 0, onSelect: n, className: r }) {
	let i = u(null), [o, c] = d(t), l = u(!1), f = u(null), p = u(null), g = a((e, t = "auto") => {
		let n = i.current;
		if (!n) return;
		let r = n.querySelector(`[data-index="${e}"]`);
		if (!r) return;
		let a = n.clientHeight, o = r.offsetTop, s = r.offsetHeight;
		l.current = !0, n.scrollTo({
			top: o - (a - s) / 2,
			behavior: t
		}), t === "smooth" ? setTimeout(() => {
			l.current = !1;
		}, 400) : requestAnimationFrame(() => {
			l.current = !1;
		});
	}, []);
	s(() => {
		g(t, "auto");
	}, [t, g]), s(() => {
		requestAnimationFrame(() => {
			g(t, "auto");
		});
	}, []);
	let _ = a(() => {
		let e = i.current;
		if (!e) return;
		let t = e.scrollTop + e.clientHeight / 2, n = 0, r = Infinity;
		return e.querySelectorAll("[data-index]").forEach((e) => {
			let i = e, a = Number(i.dataset.index);
			if (Number.isNaN(a)) return;
			let o = i.offsetTop + i.offsetHeight / 2, s = Math.abs(o - t);
			s < r && (r = s, n = a);
		}), c((e) => e === n ? e : n), n;
	}, []), v = a(() => {
		l.current || p.current === null && (p.current = requestAnimationFrame(() => {
			p.current = null;
			let e = _();
			f.current !== null && clearTimeout(f.current), f.current = setTimeout(() => {
				e !== void 0 && (l.current = !0, g(e, "smooth"), n && n(e));
			}, zu);
		}));
	}, [
		_,
		g,
		n
	]), y = a((e) => {
		n && n(e), g(e, "smooth");
	}, [n, g]);
	return s(() => () => {
		f.current !== null && clearTimeout(f.current), p.current !== null && cancelAnimationFrame(p.current);
	}, []), /* @__PURE__ */ h("div", {
		ref: i,
		className: X("picker-column", r),
		role: "listbox",
		"aria-label": "Picker column",
		onScroll: v,
		children: [
			/* @__PURE__ */ m("div", {
				style: {
					height: Ru,
					flexShrink: 0
				},
				"aria-hidden": "true"
			}),
			e.map((e, t) => {
				let n = Math.abs(t - o), r;
				return r = n === 0 ? "Medium" : n === 1 ? "Small" : "Mini", /* @__PURE__ */ m(Lu, {
					类型: r,
					selected: n === 0,
					onClick: () => y(t),
					"data-index": t,
					role: "option",
					"aria-selected": n === 0,
					children: e
				}, t);
			}),
			/* @__PURE__ */ m("div", {
				style: {
					height: Ru,
					flexShrink: 0
				},
				"aria-hidden": "true"
			})
		]
	});
}
//#endregion
//#region src/components/Selection/Picker/picker.tsx
var Vu = [
	"Time",
	"Year with date",
	"Date with time"
], Hu = {
	Time: [
		{ items: ["AM", "PM"] },
		{ items: [
			"01",
			"02",
			"03",
			"04",
			"05",
			"06",
			"07",
			"08",
			"09",
			"10",
			"11",
			"12"
		] },
		{ items: /* @__PURE__ */ "00.01.02.03.04.05.06.07.08.09.10.11.12.13.14.15.16.17.18.19.20.21.22.23.24.25.26.27.28.29.30.31.32.33.34.35.36.37.38.39.40.41.42.43.44.45.46.47.48.49.50.51.52.53.54.55.56.57.58.59".split(".") }
	],
	"Year with date": [
		{ items: [
			"2020",
			"2021",
			"2022",
			"2023",
			"2024",
			"2025",
			"2026",
			"2027",
			"2028",
			"2029",
			"2030"
		] },
		{ items: [
			"Jan",
			"Feb",
			"Mar",
			"Apr",
			"May",
			"Jun",
			"Jul",
			"Aug",
			"Sep",
			"Oct",
			"Nov",
			"Dec"
		] },
		{ items: /* @__PURE__ */ "01.02.03.04.05.06.07.08.09.10.11.12.13.14.15.16.17.18.19.20.21.22.23.24.25.26.27.28.29.30.31".split(".") }
	],
	"Date with time": [
		{ items: [
			"Mon",
			"Tue",
			"Wed",
			"Thu",
			"Fri",
			"Sat",
			"Sun"
		] },
		{ items: ["AM", "PM"] },
		{ items: [
			"01",
			"02",
			"03",
			"04",
			"05",
			"06",
			"07",
			"08",
			"09",
			"10",
			"11",
			"12"
		] },
		{ items: /* @__PURE__ */ "00.01.02.03.04.05.06.07.08.09.10.11.12.13.14.15.16.17.18.19.20.21.22.23.24.25.26.27.28.29.30.31.32.33.34.35.36.37.38.39.40.41.42.43.44.45.46.47.48.49.50.51.52.53.54.55.56.57.58.59".split(".") }
	]
};
function Uu({ 类型: e = "Time", columns: t, className: n }) {
	let r = Hu[e], i = t ?? r, [o, s] = d(() => i.map((e) => e.selectedIndex ?? Math.floor(e.items.length / 2))), c = a((e, t) => {
		s((n) => {
			let r = [...n];
			return r[e] = t, r;
		});
	}, []);
	return /* @__PURE__ */ h("div", {
		className: X("picker", `picker--${e.toLowerCase().replace(/\s+/g, "-")}`, n),
		"data-type": e,
		children: [/* @__PURE__ */ h("div", {
			className: "picker__selection-indicator",
			"aria-hidden": "true",
			children: [/* @__PURE__ */ m($, {
				尺寸: "0.5",
				className: "picker__selection-indicator-divider picker__selection-indicator-divider--top"
			}), /* @__PURE__ */ m($, {
				尺寸: "0.5",
				className: "picker__selection-indicator-divider picker__selection-indicator-divider--bottom"
			})]
		}), /* @__PURE__ */ m("div", {
			className: "picker__columns",
			children: i.map((e, t) => /* @__PURE__ */ m(Bu, {
				items: e.items,
				selectedIndex: o[t],
				onSelect: (e) => c(t, e),
				className: "picker__column"
			}, t))
		})]
	});
}
//#endregion
//#region src/components/Selection/Picker/picker-dialog.tsx
var Wu = ["open", "closed"];
function Gu({ open: e = !1, onOpenChange: t, title: n = "Select", 类型: r = "Time", columns: i, onConfirm: a, onCancel: o, confirmLabel: s = "Confirm", cancelLabel: c = "Cancel", className: l }) {
	let u = () => {
		o && o(), t && t(!1);
	};
	return e ? /* @__PURE__ */ h("div", {
		className: X("picker-dialog", l),
		role: "dialog",
		"aria-modal": "true",
		"aria-labelledby": "picker-dialog-title",
		"data-open": e,
		children: [/* @__PURE__ */ m("div", {
			className: "picker-dialog__backdrop",
			onClick: u
		}), /* @__PURE__ */ h("div", {
			className: "picker-dialog__content",
			children: [
				/* @__PURE__ */ m("div", {
					className: "picker-dialog__title",
					id: "picker-dialog-title",
					children: n
				}),
				/* @__PURE__ */ m("div", {
					className: "picker-dialog__picker-container",
					children: /* @__PURE__ */ m(Uu, {
						类型: r,
						columns: i
					})
				}),
				/* @__PURE__ */ h("div", {
					className: "picker-dialog__button-group",
					children: [
						/* @__PURE__ */ m("button", {
							className: "picker-dialog__button picker-dialog__button--cancel",
							onClick: u,
							"aria-label": c,
							children: c
						}),
						/* @__PURE__ */ m($, {
							方向: "vertical",
							尺寸: "0.5",
							className: "picker-dialog__divider",
							"aria-hidden": "true"
						}),
						/* @__PURE__ */ m("button", {
							className: "picker-dialog__button picker-dialog__button--confirm",
							onClick: () => {
								a && a(), t && t(!1);
							},
							"aria-label": s,
							children: s
						})
					]
				})
			]
		})]
	}) : null;
}
//#endregion
//#region src/components/Selection/Picker/index.ts
var Ku = /* @__PURE__ */ _({
	Picker: () => Uu,
	PickerColumn: () => Bu,
	PickerDialog: () => Gu,
	PickerItem: () => Lu,
	pickerDialogPickerTypes: () => Vu,
	pickerDialogStates: () => Wu,
	pickerItemTypes: () => Iu,
	pickerTypes: () => Vu
}), qu = {
	Time: "Friday, July 7, 2025",
	"Year with date": "Friday, July 7, 2025",
	"Date with time": "Friday, July 7, 2025"
}, Ju = {
	Time: [
		{
			items: ["AM", "PM"],
			selectedIndex: 0
		},
		{
			items: [
				"06",
				"07",
				"08",
				"09",
				"10"
			],
			selectedIndex: 2
		},
		{
			items: [
				"06",
				"07",
				"08",
				"09",
				"10"
			],
			selectedIndex: 2
		}
	],
	"Year with date": [
		{
			items: [
				"2021",
				"2022",
				"2023",
				"2024",
				"2025"
			],
			selectedIndex: 2
		},
		{
			items: [
				"Sep",
				"Oct",
				"Nov",
				"Dec",
				"Jan"
			],
			selectedIndex: 2
		},
		{
			items: [
				"15",
				"16",
				"17",
				"18",
				"19"
			],
			selectedIndex: 2
		}
	],
	"Date with time": [
		{
			items: [
				"July 5",
				"July 6",
				"Today",
				"July 8",
				"July 9"
			],
			selectedIndex: 2,
			titleValues: [
				"Saturday, July 5, 2025",
				"Sunday, July 6, 2025",
				"Friday, July 7, 2025",
				"Tuesday, July 8, 2025",
				"Wednesday, July 9, 2025"
			]
		},
		{
			items: ["AM", "PM"],
			selectedIndex: 0
		},
		{
			items: [
				"06",
				"07",
				"08",
				"09",
				"10"
			],
			selectedIndex: 2
		},
		{
			items: [
				"06",
				"07",
				"08",
				"09",
				"10"
			],
			selectedIndex: 2
		}
	]
};
function Yu(e, t) {
	return t?.length ? e.map((e, n) => t[n] ?? e.selectedIndex ?? 0) : e.map((e) => e.selectedIndex ?? 0);
}
function Xu(e, t) {
	return e.map((e, n) => e.items[t[n]] ?? e.items[0] ?? "");
}
function Zu(e, t, n, r) {
	if (r) return r;
	let i = e[0];
	if (!i) return "";
	let a = t[0] ?? i.selectedIndex ?? 0;
	return i.titleValues?.[a] ?? qu[n] ?? i.items[a] ?? i.items[0] ?? "";
}
function Qu(e, t) {
	return X("hm-floating-picker-dialog__column", `hm-floating-picker-dialog__column--${t + 1}`, e === "Date with time" && "hm-floating-picker-dialog__column--date-with-time");
}
function $u(e, t) {
	return e === "emphasize-port" ? t : t === 3 ? 2 : t;
}
function ed({ 通透度: e = "标准", 类型: t = "Time", ButtonGroup类型: n = "normal", ButtonGroup个数: r = 2, 标题: i, columns: a, selectedIndices: o, defaultSelectedIndices: c, onSelectedIndicesChange: l, 按钮文案: u = "BUTTON", 取消文案: f = "Cancel", 确认文案: g = "OK", onCancel: _, onConfirm: v, className: y, ...b }) {
	let x = a ?? Ju[t], S = o !== void 0, [C, w] = d(() => Yu(x, c));
	s(() => {
		S || w(Yu(x, c));
	}, [
		x,
		S,
		c
	]);
	let T = S ? Yu(x, o) : C, E = Xu(x, T), D = Zu(x, T, t, i), O = $u(n, r), k = (e, t) => {
		let n = T.map((n, r) => r === e ? t : n);
		S || w(n), l?.(n, Xu(x, n));
	};
	return /* @__PURE__ */ h("div", {
		className: X("hm-floating-picker-dialog", "hm-material-style-layer-floating-thick-effect-1", y),
		"data-opacity": e,
		"data-button-group-type": n,
		"data-button-group-count": O,
		...b,
		children: [
			/* @__PURE__ */ m("div", { className: "hm-material-style-layer hm-material-style-layer-floating-thick-fill-1" }),
			/* @__PURE__ */ m("div", { className: "hm-material-style-layer hm-material-style-layer-floating-thick-fill-2" }),
			/* @__PURE__ */ m("div", { className: "hm-material-style-layer hm-material-style-layer-floating-thick-effect-2" }),
			/* @__PURE__ */ m("div", { className: "hm-material-style-layer hm-material-style-layer-floating-thick-effect-3" }),
			/* @__PURE__ */ m("div", { className: "hm-material-style-layer hm-material-style-layer-floating-thick-effect-4" }),
			/* @__PURE__ */ m("div", { className: "hm-material-style-layer hm-material-style-layer-floating-thick-effect-5" }),
			/* @__PURE__ */ m("div", { className: "hm-material-style-layer hm-material-style-layer-floating-thick-effect-6" }),
			/* @__PURE__ */ m("div", { className: "hm-material-style-layer hm-material-style-layer-floating-thick-effect-7" }),
			/* @__PURE__ */ m("div", { className: "hm-material-style-layer hm-material-style-layer-floating-thick-effect-8" }),
			/* @__PURE__ */ m("h2", {
				className: "hm-floating-picker-dialog__title",
				children: D
			}),
			/* @__PURE__ */ h("div", {
				className: "hm-floating-picker-dialog__picker",
				children: [/* @__PURE__ */ h("div", {
					className: "hm-floating-picker-dialog__selection-band",
					"aria-hidden": "true",
					children: [/* @__PURE__ */ m($, {
						尺寸: "0.5",
						颜色: "rgba(0, 0, 0, 0.08)",
						className: "hm-floating-picker-dialog__selection-divider hm-floating-picker-dialog__selection-divider--top"
					}), /* @__PURE__ */ m($, {
						尺寸: "0.5",
						颜色: "rgba(0, 0, 0, 0.08)",
						className: "hm-floating-picker-dialog__selection-divider hm-floating-picker-dialog__selection-divider--bottom"
					})]
				}), /* @__PURE__ */ m("div", {
					className: "hm-floating-picker-dialog__columns",
					"data-picker-type": t,
					children: x.map((e, n) => /* @__PURE__ */ m(Bu, {
						className: Qu(t, n),
						items: e.items,
						selectedIndex: T[n] ?? e.selectedIndex ?? 0,
						onSelect: (e) => k(n, e)
					}, `${n}-${e.items.join("|")}`))
				})]
			}),
			/* @__PURE__ */ h("div", {
				className: X("hm-floating-picker-dialog__actions", `hm-floating-picker-dialog__actions--${n}`),
				"data-button-count": O,
				children: [
					n === "normal" ? /* @__PURE__ */ h(p, { children: [O === 2 ? /* @__PURE__ */ h(p, { children: [/* @__PURE__ */ m("button", {
						className: "hm-floating-picker-dialog__button hm-floating-picker-dialog__button--text",
						onClick: _,
						type: "button",
						children: f
					}), /* @__PURE__ */ m($, {
						方向: "vertical",
						尺寸: "0.5",
						颜色: "rgba(0, 0, 0, 0.08)",
						className: "hm-floating-picker-dialog__actions-divider",
						"aria-hidden": "true"
					})] }) : null, /* @__PURE__ */ m("button", {
						className: "hm-floating-picker-dialog__button hm-floating-picker-dialog__button--text",
						onClick: () => v?.(E, T),
						type: "button",
						children: O === 2 ? g : u
					})] }) : null,
					n === "emphasize" ? /* @__PURE__ */ h(p, { children: [O === 2 ? /* @__PURE__ */ m("button", {
						className: "hm-floating-picker-dialog__button hm-floating-picker-dialog__button--text",
						onClick: _,
						type: "button",
						children: u
					}) : null, /* @__PURE__ */ m("button", {
						className: "hm-floating-picker-dialog__button hm-floating-picker-dialog__button--primary",
						onClick: () => v?.(E, T),
						type: "button",
						children: u
					})] }) : null,
					n === "emphasize-port" ? /* @__PURE__ */ h(p, { children: [/* @__PURE__ */ m("button", {
						className: "hm-floating-picker-dialog__button hm-floating-picker-dialog__button--primary",
						onClick: () => v?.(E, T),
						type: "button",
						children: u
					}), Array.from({ length: O - 1 }).map((e, t) => /* @__PURE__ */ m("button", {
						className: "hm-floating-picker-dialog__button hm-floating-picker-dialog__button--text",
						onClick: _,
						type: "button",
						children: u
					}, t))] }) : null
				]
			})
		]
	});
}
//#endregion
//#region src/components/Selection/FloatingPickerDialog/floating-picker-dialog.constants.ts
var td = [
	"强",
	"标准",
	"降档",
	"弱"
], nd = /* @__PURE__ */ _({
	FloatingPickerDialog: () => ed,
	floatingPickerDialogOpacities: () => td
}), rd = [
	2,
	3,
	4,
	5
], id = [
	"弱",
	"标准",
	"强",
	"降档"
], ad = [
	"Enable",
	"activated",
	"Selected"
], od = "segmented_button_highlight";
function sd({ 组数: e = 3, 通透度: t = "弱", 状态: n = "activated", Text: r = !0, Icon: i = !0, items: a, selectedIndex: o, defaultSelectedIndex: s = 1, onSelectedIndexChange: c, className: l, ...u }) {
	let f = e, p = cd(a, f), [g, _] = d(() => ld(s, p.length)), v = ld(o ?? g, p.length), y = (e) => {
		o === void 0 && _(e), c?.(e);
	};
	return /* @__PURE__ */ h("div", {
		className: X("hm-floating-segmented-button", "hm-material-style-layer-floating-thin-effect-2", l),
		"data-count": String(f),
		"data-transparency": t,
		"data-item-state": n,
		...u,
		children: [
			/* @__PURE__ */ m("div", { className: "hm-material-style-layer hm-material-style-layer-floating-thin-fill-1" }),
			/* @__PURE__ */ m("div", { className: "hm-material-style-layer hm-material-style-layer-floating-thin-fill-2" }),
			/* @__PURE__ */ m("div", { className: "hm-material-style-layer hm-material-style-layer-floating-thin-effect-1" }),
			/* @__PURE__ */ m("div", { className: "hm-material-style-layer hm-material-style-layer-floating-thin-effect-3" }),
			/* @__PURE__ */ m("div", { className: "hm-material-style-layer hm-material-style-layer-floating-thin-effect-4" }),
			/* @__PURE__ */ m("div", { className: "hm-material-style-layer hm-material-style-layer-floating-thin-effect-5" }),
			/* @__PURE__ */ m("div", { className: "hm-material-style-layer hm-material-style-layer-floating-thin-effect-6" }),
			/* @__PURE__ */ m("div", { className: "hm-material-style-layer hm-material-style-layer-floating-thin-effect-7" }),
			/* @__PURE__ */ m("div", { className: "hm-material-style-layer hm-material-style-layer-floating-thin-effect-8" }),
			/* @__PURE__ */ m("div", {
				className: "hm-floating-segmented-button__rail",
				role: "tablist",
				style: { gridTemplateColumns: `repeat(${p.length}, minmax(0, 1fr))` },
				children: p.map((e, t) => {
					let a = e.状态 ?? (t === v ? n : "Enable"), o = a !== "Enable", s = e.Icon ?? i, c = e.Text ?? r, l = e.label ?? "Tabs";
					return /* @__PURE__ */ h("button", {
						type: "button",
						role: "tab",
						"aria-selected": o,
						className: "hm-floating-segmented-button__item",
						"data-selected": o ? "true" : "false",
						"data-state": a,
						"data-icon": s ? "true" : "false",
						"data-text": c ? "true" : "false",
						onClick: () => y(t),
						children: [s ? /* @__PURE__ */ m("span", {
							className: "hm-floating-segmented-button__icon",
							"aria-hidden": "true",
							children: e.icon ?? /* @__PURE__ */ m(Z, {
								name: od,
								size: 24
							})
						}) : null, c ? /* @__PURE__ */ m("span", {
							className: "hm-floating-segmented-button__label",
							children: l
						}) : null]
					}, `${l}-${t}`);
				})
			})
		]
	});
}
function cd(e, t) {
	return e?.length ? e.slice(0, t) : Array.from({ length: t }, () => ({ label: "Tabs" }));
}
function ld(e, t) {
	return t <= 0 ? 0 : Math.min(Math.max(e, 0), t - 1);
}
//#endregion
//#region src/components/Selection/FloatingSegmentedButton/index.ts
var ud = /* @__PURE__ */ _({
	FloatingSegmentedButton: () => sd,
	floatingSegmentedButtonItem状态: () => ad,
	floatingSegmentedButton组数: () => rd,
	floatingSegmentedButton通透度: () => id
}), dd = [
	1,
	2,
	3,
	4,
	5
], fd = i(function({ value: e, defaultValue: t, onChange: n, max: r = 5, disabled: i = !1, readOnly: o = !1, className: s, ...c }, l) {
	let f = e !== void 0, [p, h] = d(t ?? 5), [g, _] = d(0), v = u(null), y = a((e) => {
		v.current = e, typeof l == "function" ? l(e) : l && (l.current = e);
	}, [l]), b = f ? e : p, x = !i && !o && n !== void 0, S = a((e) => {
		let t = e;
		f || h(t), n?.(t);
	}, [f, n]), C = a((e) => {
		if (!x) return;
		let t = b;
		e.key === "ArrowRight" || e.key === "ArrowUp" ? (e.preventDefault(), t = Math.min(5, b + 1)) : (e.key === "ArrowLeft" || e.key === "ArrowDown") && (e.preventDefault(), t = Math.max(1, b - 1)), t !== b && (S(t), (v.current?.children[t - 1])?.focus());
	}, [
		x,
		b,
		S
	]);
	return /* @__PURE__ */ m("div", {
		ref: y,
		className: X("pixso-rating-phone", i && "pixso-rating-phone--disabled", o && "pixso-rating-phone--readonly", s),
		role: x ? "radiogroup" : "img",
		"aria-label": `Rating: ${b} out of ${r}`,
		"aria-disabled": i || void 0,
		onKeyDown: C,
		...c,
		children: Array.from({ length: r }, (e, t) => {
			let n = t + 1;
			return /* @__PURE__ */ m("button", {
				type: "button",
				className: X("pixso-rating-phone__star", (x && g > 0 ? n <= g : n <= b) ? "pixso-rating-phone__star--active" : "pixso-rating-phone__star--inactive"),
				role: x ? "radio" : void 0,
				"aria-checked": x ? n === b : void 0,
				"aria-label": `${n} star${n > 1 ? "s" : ""}`,
				disabled: i,
				tabIndex: x && n === b ? 0 : -1,
				onClick: () => {
					x && S(n);
				},
				onMouseEnter: () => {
					x && _(n);
				},
				onMouseLeave: () => {
					x && _(0);
				},
				children: /* @__PURE__ */ m(Z, {
					className: "pixso-rating-phone__star-icon",
					name: "star_fill",
					size: 28
				})
			}, n);
		})
	});
}), pd = /* @__PURE__ */ _({
	RatingPhone: () => fd,
	ratingValues: () => dd
}), md = ["ON", "OFF"], hd = ["on", "off"], gd = [
	2,
	3,
	4,
	5
], _d = [
	"Enable",
	"activated",
	"Selected"
], vd = [
	"Left",
	"Mid",
	"Right"
];
function yd({ multiSelection: e = "OFF", Icon: t = "off", 组数: n = 3, items: r, selectedIndex: i = 0, selectedIndices: a = [], onSelect: o, onMultiSelect: s, className: c }) {
	let l = r ?? [
		"Tab 1",
		"Tab 2",
		"Tab 3",
		"Tab 4",
		"Tab 5"
	].slice(0, n).map((e) => ({ label: e })), u = Math.min(l.length, n), d = (t) => {
		if (e === "OFF") o?.(t);
		else {
			let e = a.includes(t) ? a.filter((e) => e !== t) : [...a, t];
			s?.(e);
		}
	}, f = (t) => l[t]?.状态 ? l[t].状态 : e === "OFF" ? t === i ? "activated" : "Enable" : a.includes(t) ? "Selected" : "Enable";
	return /* @__PURE__ */ m("div", {
		className: X("segmented-button", `segmented-button--${e.toLowerCase()}`, `segmented-button--icon-${t}`, `segmented-button--count-${n}`, c),
		role: "tablist",
		"data-multi-selection": e,
		"data-icon": t,
		"data-group-count": n,
		children: l.slice(0, u).map((e, n) => {
			let r = bd(n, u), i = f(n), a = t === "on";
			return /* @__PURE__ */ m(Sd, {
				位置: r,
				状态: i,
				label: e.label,
				icon: e.icon,
				showIcon: a,
				onClick: () => d(n)
			}, n);
		})
	});
}
function bd(e, t) {
	return t <= 1 ? "Mid" : e === 0 ? "Left" : e === t - 1 ? "Right" : "Mid";
}
var xd = "segmented_button_highlight";
function Sd({ 位置: e = "Mid", 状态: t = "Enable", label: n = "Tabs", icon: r, showIcon: i = !1, onClick: a, className: o }) {
	return /* @__PURE__ */ h("button", {
		type: "button",
		role: "tab",
		"aria-selected": t === "activated" || t === "Selected",
		className: X("segmented-button__item", `segmented-button__item--${e.toLowerCase()}`, `segmented-button__item--state-${t.toLowerCase()}`, o),
		onClick: a,
		"data-position": e,
		"data-state": t,
		children: [
			i && r === void 0 && /* @__PURE__ */ m(Z, {
				name: xd,
				size: 24,
				className: "segmented-button__indicator"
			}),
			i && r !== void 0 && /* @__PURE__ */ m("span", {
				className: "segmented-button__icon",
				children: r
			}),
			/* @__PURE__ */ m("span", {
				className: "segmented-button__label",
				children: n
			})
		]
	});
}
//#endregion
//#region src/components/Selection/SegmentedButton/index.ts
var Cd = /* @__PURE__ */ _({
	SegmentedButton: () => yd,
	SegmentedButtonItemInternal: () => Sd,
	groupCountValues: () => gd,
	iconVisibilityValues: () => hd,
	multiSelectionValues: () => md,
	positionValues: () => vd,
	stateValues: () => _d
}), wd = [
	"Basic",
	"Scale",
	"Icon",
	"Value with text change",
	"Value",
	"Icon with title",
	"Bubble",
	"Title",
	"Textview"
], Td = [
	"Enabled",
	"Hover",
	"Focus"
], Ed = [
	"enabled",
	"icon",
	"focus",
	"hover",
	"Value",
	"Bubble",
	"Scale"
], Dd = 42, Od = {
	Basic: 336,
	Scale: 336,
	Icon: 224,
	"Value with text change": 250,
	Value: 336,
	"Icon with title": 272,
	Bubble: 336,
	Title: 312,
	Textview: 312
}, kd = {
	enabled: {
		类型: "Basic",
		状态: "Enabled"
	},
	hover: {
		类型: "Basic",
		状态: "Hover"
	},
	focus: {
		类型: "Basic",
		状态: "Focus"
	},
	Scale: {
		类型: "Scale",
		状态: "Enabled"
	},
	icon: {
		类型: "Icon",
		状态: "Enabled"
	},
	Value: {
		类型: "Value",
		状态: "Enabled"
	},
	Bubble: {
		类型: "Bubble",
		状态: "Enabled"
	}
};
function Ad(e, t, n) {
	return Math.max(t, Math.min(n, e));
}
function jd({ ...e }) {
	return /* @__PURE__ */ m(Nd, {
		...e,
		trackStyle: "Thick"
	});
}
function Md({ 状态: e = "enabled", ...t }) {
	let n = kd[e];
	return /* @__PURE__ */ m(Nd, {
		...t,
		类型: n.类型,
		状态: n.状态,
		trackStyle: "Thin"
	});
}
function Nd({ 类型: e = "Basic", 状态: t = "Enabled", layout: n = "fixed", 宽度: r, trackStyle: i, value: o, defaultValue: s = Dd, min: c = 0, max: l = 100, step: u = 1, disabled: f = !1, onChange: g, title: _ = "Title", progressValue: v = "Progress value", leftLabel: y = "A", rightLabel: b = "A", smallLabel: x = "Small", bigLabel: S = "Big", icons: C, className: w, ...T }) {
	let [E, D] = d(s), O = o !== void 0, k = Ad(O ? o : E, c, l), A = a((e) => {
		let t = Ad(e, c, l);
		O || D(t), g?.(t);
	}, [
		O,
		g,
		c,
		l
	]), j = C ?? [/* @__PURE__ */ m(Z, {
		className: "hm-slider__icon-svg",
		name: "sun_min",
		size: 24
	}), /* @__PURE__ */ m(Z, {
		className: "hm-slider__icon-svg",
		name: "sun_max",
		size: 24
	})], M = Math.round((k - c) / (l - c) * 100), N = n === "contained" || r === "自适应";
	return /* @__PURE__ */ h("div", {
		className: X("hm-slider", `hm-slider--${Fd(e)}`, `hm-slider--track-${i.toLowerCase()}`, N && "hm-slider--contained", f && "hm-slider--disabled", w),
		"data-layout": N ? "contained" : "fixed",
		...T,
		children: [
			e === "Basic" && /* @__PURE__ */ m(Pd, {
				trackWidth: Od.Basic,
				trackStyle: i,
				value: k,
				pct: M,
				min: c,
				max: l,
				step: u,
				disabled: f,
				状态: t,
				onChange: A,
				fullWidth: N
			}),
			e === "Scale" && /* @__PURE__ */ h("div", {
				className: "hm-slider__scale",
				children: [/* @__PURE__ */ m(Pd, {
					trackWidth: Od.Scale,
					trackStyle: i,
					value: k,
					pct: M,
					min: c,
					max: l,
					step: u,
					disabled: f,
					状态: t,
					onChange: A,
					fullWidth: N
				}), /* @__PURE__ */ m("div", {
					"aria-hidden": "true",
					className: "hm-slider__ticks",
					children: Array.from({ length: 8 }).map((e, t) => /* @__PURE__ */ m("span", { className: "hm-slider__tick-dot" }, t))
				})]
			}),
			e === "Icon" && /* @__PURE__ */ h("div", {
				className: "hm-slider__inline-row hm-slider__inline-row--icon",
				children: [
					/* @__PURE__ */ m("span", {
						className: "hm-slider__icon-slot",
						children: j[0]
					}),
					/* @__PURE__ */ m(Pd, {
						trackWidth: Od.Icon,
						trackStyle: i,
						value: k,
						pct: M,
						min: c,
						max: l,
						step: u,
						disabled: f,
						状态: t,
						onChange: A,
						fullWidth: N || i === "Thin"
					}),
					/* @__PURE__ */ m("span", {
						className: "hm-slider__icon-slot",
						children: j[1]
					})
				]
			}),
			e === "Value with text change" && /* @__PURE__ */ h("div", {
				className: "hm-slider__inline-row hm-slider__inline-row--value-text",
				children: [
					/* @__PURE__ */ m("span", {
						className: "hm-slider__edge-label",
						children: y
					}),
					/* @__PURE__ */ m(Pd, {
						trackWidth: Od["Value with text change"],
						trackStyle: i,
						value: k,
						pct: M,
						min: c,
						max: l,
						step: u,
						disabled: f,
						状态: t,
						onChange: A,
						fullWidth: N
					}),
					/* @__PURE__ */ m("span", {
						className: "hm-slider__edge-label hm-slider__edge-label--right",
						children: b
					})
				]
			}),
			e === "Value" && /* @__PURE__ */ h(p, { children: [/* @__PURE__ */ m(Pd, {
				trackWidth: Od.Value,
				trackStyle: i,
				value: k,
				pct: M,
				min: c,
				max: l,
				step: u,
				disabled: f,
				状态: t,
				onChange: A,
				fullWidth: N
			}), /* @__PURE__ */ m("div", {
				className: "hm-slider__number-scale",
				children: [
					0,
					20,
					40,
					60,
					80,
					100
				].map((e) => /* @__PURE__ */ m("span", {
					className: "hm-slider__number-label",
					children: e
				}, e))
			})] }),
			e === "Icon with title" && /* @__PURE__ */ h(p, { children: [/* @__PURE__ */ h("div", {
				className: "hm-slider__title-row hm-slider__title-row--icon-title",
				children: [/* @__PURE__ */ m("span", {
					className: "hm-slider__icon-slot",
					children: j[0]
				}), /* @__PURE__ */ m("span", {
					className: "hm-slider__title",
					children: _
				})]
			}), /* @__PURE__ */ m("div", {
				className: "hm-slider__icon-title-rail-shell",
				children: /* @__PURE__ */ m(Pd, {
					trackWidth: Od["Icon with title"],
					trackStyle: i,
					value: k,
					pct: M,
					min: c,
					max: l,
					step: u,
					disabled: f,
					状态: t,
					onChange: A,
					fullWidth: N
				})
			})] }),
			e === "Bubble" && /* @__PURE__ */ h("div", {
				className: "hm-slider__bubble-layout",
				children: [/* @__PURE__ */ m("div", {
					className: "hm-slider__bubble",
					style: { "--slider-progress": `${M}%` },
					children: /* @__PURE__ */ m("span", {
						className: "hm-slider__bubble-text",
						children: `${M}%`
					})
				}), /* @__PURE__ */ m(Pd, {
					trackWidth: Od.Bubble,
					trackStyle: i,
					value: k,
					pct: M,
					min: c,
					max: l,
					step: u,
					disabled: f,
					状态: t,
					onChange: A,
					fullWidth: N
				})]
			}),
			e === "Title" && /* @__PURE__ */ h(p, { children: [/* @__PURE__ */ h("div", {
				className: "hm-slider__title-row hm-slider__title-row--summary",
				children: [/* @__PURE__ */ m("span", {
					className: "hm-slider__title",
					children: _
				}), /* @__PURE__ */ m("span", {
					className: "hm-slider__progress-label",
					children: v
				})]
			}), /* @__PURE__ */ m(Pd, {
				trackWidth: Od.Title,
				trackStyle: i,
				value: k,
				pct: M,
				min: c,
				max: l,
				step: u,
				disabled: f,
				状态: t,
				onChange: A,
				fullWidth: N
			})] }),
			e === "Textview" && /* @__PURE__ */ h(p, { children: [/* @__PURE__ */ m(Pd, {
				trackWidth: Od.Textview,
				trackStyle: i,
				value: k,
				pct: M,
				min: c,
				max: l,
				step: u,
				disabled: f,
				状态: t,
				onChange: A,
				fullWidth: N
			}), /* @__PURE__ */ h("div", {
				className: "hm-slider__textview-row",
				children: [/* @__PURE__ */ m("span", {
					className: "hm-slider__endpoint-label",
					children: x
				}), /* @__PURE__ */ m("span", {
					className: "hm-slider__endpoint-label",
					children: S
				})]
			})] })
		]
	});
}
function Pd({ trackWidth: e, trackStyle: t, value: n, pct: r, min: i, max: o, step: c, disabled: l, 状态: f, onChange: g, fullWidth: _ = !1 }) {
	let v = u(null), y = u(null), [b, x] = d(!1), [S, C] = d(!1), [w, T] = d(!1), E = f === "Enabled" ? S ? "Focus" : b || w ? "Hover" : "Enabled" : f, D = a((e) => {
		let t = y.current?.getBoundingClientRect();
		if (!t) return;
		let n = i + (e - t.left) / t.width * (o - i);
		g(Ad(Math.round(n / c) * c, i, o));
	}, [
		g,
		i,
		o,
		c
	]);
	s(() => {
		if (!w || l) return;
		let e = (e) => D(e.clientX), t = (e) => D(e.touches[0]?.clientX ?? 0), n = () => T(!1);
		return window.addEventListener("mousemove", e), window.addEventListener("mouseup", n), window.addEventListener("touchmove", t, { passive: !0 }), window.addEventListener("touchend", n), () => {
			window.removeEventListener("mousemove", e), window.removeEventListener("mouseup", n), window.removeEventListener("touchmove", t), window.removeEventListener("touchend", n);
		};
	}, [
		w,
		l,
		D
	]);
	let O = _ ? void 0 : { "--slider-track-width": `${e}px` };
	return /* @__PURE__ */ m("div", {
		className: X("hm-slider__rail-shell", _ && "hm-slider__rail-shell--full"),
		style: O,
		children: /* @__PURE__ */ h("div", {
			className: X("hm-slider__track", `hm-slider__track--${E.toLowerCase()}`),
			ref: y,
			style: { "--slider-progress": `${r}%` },
			children: [
				/* @__PURE__ */ m("input", {
					"aria-label": "slider",
					className: "hm-slider__range",
					disabled: l,
					max: o,
					min: i,
					onBlur: () => C(!1),
					onChange: (e) => g(Number(e.target.value)),
					onFocus: () => C(!0),
					onMouseDown: (e) => {
						l || (T(!0), D(e.clientX));
					},
					onMouseEnter: () => x(!0),
					onMouseLeave: () => x(!1),
					onTouchStart: (e) => {
						l || (T(!0), D(e.touches[0]?.clientX ?? 0));
					},
					ref: v,
					step: c,
					type: "range",
					value: n
				}),
				t === "Thin" && /* @__PURE__ */ h(p, { children: [
					/* @__PURE__ */ m("div", { className: "hm-slider__track-fill" }),
					/* @__PURE__ */ m("div", { className: "hm-slider__thumb-outer" }),
					/* @__PURE__ */ m("div", { className: "hm-slider__thumb" })
				] }),
				E === "Focus" && /* @__PURE__ */ m("span", { className: "hm-slider__focus-ring" })
			]
		})
	});
}
function Fd(e) {
	return e.replace(/\s+/g, "-").toLowerCase();
}
//#endregion
//#region src/components/Selection/Slider/index.ts
var Id = /* @__PURE__ */ _({
	Slider: () => jd,
	SliderSeekbar: () => Md,
	sliderSeekbarStates: () => Ed,
	sliderStates: () => Td,
	sliderTypes: () => wd
}), Ld = ["port", "land"], Rd = [
	{
		kind: "item",
		label: "#"
	},
	{ kind: "star" },
	{
		kind: "item",
		label: "A"
	},
	{
		kind: "item",
		label: "B"
	},
	{
		kind: "item",
		label: "C"
	},
	{
		kind: "item",
		label: "D"
	},
	{
		kind: "item",
		label: "E"
	},
	{
		kind: "item",
		label: "F"
	},
	{
		kind: "item",
		label: "G",
		状态: "activated"
	},
	{
		kind: "item",
		label: "H"
	},
	{
		kind: "item",
		label: "I"
	},
	{
		kind: "item",
		label: "J",
		状态: "hover"
	},
	{
		kind: "item",
		label: "K"
	},
	{
		kind: "item",
		label: "L"
	},
	{
		kind: "item",
		label: "M"
	},
	{
		kind: "item",
		label: "N"
	},
	{
		kind: "item",
		label: "O"
	},
	{
		kind: "item",
		label: "P"
	},
	{
		kind: "item",
		label: "Q"
	},
	{
		kind: "item",
		label: "R"
	},
	{
		kind: "item",
		label: "S"
	},
	{
		kind: "item",
		label: "T"
	},
	{
		kind: "item",
		label: "U"
	},
	{
		kind: "item",
		label: "V"
	},
	{
		kind: "item",
		label: "W"
	},
	{
		kind: "item",
		label: "X"
	},
	{
		kind: "item",
		label: "Y"
	},
	{
		kind: "item",
		label: "Z"
	}
], zd = [
	{
		kind: "item",
		label: "#"
	},
	{
		kind: "item",
		label: "A"
	},
	{ kind: "dot" },
	{
		kind: "item",
		label: "G",
		状态: "activated"
	},
	{ kind: "dot" },
	{
		kind: "item",
		label: "J"
	},
	{ kind: "dot" },
	{
		kind: "item",
		label: "O"
	},
	{ kind: "dot" },
	{
		kind: "item",
		label: "S"
	},
	{ kind: "dot" },
	{
		kind: "item",
		label: "W",
		状态: "hover"
	},
	{ kind: "dot" },
	{
		kind: "item",
		label: "Z"
	}
];
function Bd({ active: e, label: t, onSelect: n }) {
	return /* @__PURE__ */ m("button", {
		"aria-current": e ? "true" : void 0,
		className: X("alphabet-indexer__item", e ? "alphabet-indexer__item--activated" : "alphabet-indexer__item--enabled"),
		"data-index-label": t,
		onClick: () => n(t),
		type: "button",
		children: /* @__PURE__ */ m("span", {
			className: "alphabet-indexer__label",
			children: t
		})
	});
}
function Vd() {
	return /* @__PURE__ */ m("div", {
		className: "alphabet-indexer__dot",
		"aria-hidden": "true"
	});
}
function Hd() {
	return /* @__PURE__ */ m("div", {
		className: "alphabet-indexer__star",
		"aria-hidden": "true",
		children: /* @__PURE__ */ m("svg", {
			className: "alphabet-indexer__star-icon",
			fill: "none",
			viewBox: "0 0 9 8.75",
			xmlns: "http://www.w3.org/2000/svg",
			children: /* @__PURE__ */ m("path", {
				d: "M4.98482 0.290323L5.95794 2.29312C6.03469 2.4518 6.18011 2.56264 6.34926 2.59585L6.37358 2.60006L8.52711 2.91867C8.97182 2.98391 9.15415 3.53135 8.84886 3.85807L7.27734 5.41867C7.15292 5.54157 7.09295 5.71605 7.11419 5.88921L7.48552 8.09365C7.5604 8.54424 7.10413 8.88962 6.70373 8.69408L4.75842 7.65547C4.60498 7.57374 4.42369 7.56966 4.26869 7.64321L2.31919 8.68274C1.92075 8.89512 1.45557 8.56097 1.51479 8.11391L1.88561 5.91371C1.91364 5.73943 1.86223 5.56382 1.74441 5.43602L0.167085 3.87449C-0.133338 3.57739 -0.00566664 3.07703 0.366969 2.94547L0.472888 2.9194L2.62642 2.60225C2.79734 2.57656 2.94677 2.47085 3.03068 2.31851L4.00612 0.312226C4.20494 -0.0966416 4.77283 -0.103943 4.98482 0.290323ZM3.92972 2.75751L4.50016 1.58101L5.05856 2.72995C5.27116 3.16952 5.67821 3.48317 6.15675 3.57713L7.50916 3.77801L6.573 4.70898C6.22968 5.04809 6.06285 5.53037 6.12179 6.01094L6.34916 7.37101L5.22972 6.77342C4.79655 6.54269 4.28186 6.53015 3.84011 6.7398L2.65316 7.37101L2.87184 6.08008C2.94953 5.59721 2.80673 5.11284 2.47983 4.75823L2.44559 4.7224L1.49316 3.77901L2.77228 3.59159C3.25542 3.51897 3.6731 3.22518 3.90676 2.80099L3.92972 2.75751Z",
				fill: "currentColor",
				fillRule: "evenodd"
			})
		})
	});
}
function Ud({ 类型: e = "port", activeLabel: t, className: n, defaultActiveLabel: r = "G", labels: i, onIndexPressChange: a, onIndexPressEnd: o, onIndexPressStart: s, onIndexSelect: c, ...l }) {
	let [f, p] = d(r), h = u(!1), g = u(!1), _ = t ?? f, v = i === void 0 ? e === "port" ? Rd : zd : i.map((e) => ({
		kind: "item",
		label: e
	})), y = (e) => {
		t === void 0 && p(e), c?.(e);
	}, b = (e) => {
		if (g.current) {
			g.current = !1;
			return;
		}
		y(e);
	}, x = (e) => {
		let t = Wd(e.target);
		t && (h.current = !0, g.current = !0, e.currentTarget.setPointerCapture(e.pointerId), y(t), s?.(t));
	}, S = (e) => {
		if (!h.current) return;
		let t = Gd(e.clientX, e.clientY);
		t && a?.(t);
	}, C = (e) => {
		h.current && (h.current = !1, o?.(), e.currentTarget.hasPointerCapture(e.pointerId) && e.currentTarget.releasePointerCapture(e.pointerId));
	};
	return /* @__PURE__ */ m("div", {
		...l,
		className: X("alphabet-indexer", `alphabet-indexer--${e}`, n),
		onPointerCancel: C,
		onPointerDown: x,
		onPointerMove: S,
		onPointerUp: C,
		children: v.map((e, t) => e.kind === "dot" ? /* @__PURE__ */ m(Vd, {}, `dot-${t}`) : e.kind === "star" ? /* @__PURE__ */ m(Hd, {}, `star-${t}`) : /* @__PURE__ */ m(Bd, {
			active: e.label === _,
			label: e.label,
			onSelect: b
		}, `${e.label}-${t}`))
	});
}
function Wd(e) {
	return (e instanceof Element ? e : null)?.closest(".alphabet-indexer__item")?.dataset.indexLabel;
}
function Gd(e, t) {
	return document.elementFromPoint(e, t)?.closest(".alphabet-indexer__item")?.dataset.indexLabel;
}
//#endregion
//#region src/components/Views/AlphabetIndexer/index.ts
var Kd = /* @__PURE__ */ _({
	AlphabetIndexer: () => Ud,
	alphabetIndexerTypes: () => Ld
}), qd = ["Latin", "cn"], Jd = [
	{
		text: "G",
		状态: "activated"
	},
	{
		text: "古",
		状态: "enabled"
	},
	{
		text: "顾",
		状态: "enabled"
	}
];
function Yd({ activeIndex: e, items: t, onItemSelect: n }) {
	return /* @__PURE__ */ m("div", {
		className: "hm-alphabet-indexer-lable__cn-panel",
		children: t.map((t, r) => {
			let i = e === void 0 ? t.状态 === "activated" : r === e;
			return /* @__PURE__ */ m("button", {
				"aria-pressed": i,
				className: X("hm-alphabet-indexer-lable__cn-item", i && "hm-alphabet-indexer-lable__cn-item--activated"),
				onClick: () => n?.(t, r),
				type: "button",
				children: /* @__PURE__ */ m("span", {
					className: "hm-alphabet-indexer-lable__text",
					children: t.text
				})
			}, `${t.text}-${r}`);
		})
	});
}
function Xd({ value: e }) {
	return /* @__PURE__ */ m("div", {
		className: "hm-alphabet-indexer-lable__latin-chip",
		children: /* @__PURE__ */ m("span", {
			className: "hm-alphabet-indexer-lable__text",
			children: e
		})
	});
}
function Zd({ 类型: e = "Latin", value: t = "G", items: n = Jd, activeIndex: r, onItemSelect: i, className: a, ...o }) {
	return /* @__PURE__ */ m("div", {
		className: X("hm-alphabet-indexer-lable", `hm-alphabet-indexer-lable--type-${e.toLowerCase()}`, a),
		"data-type": e,
		...o,
		children: e === "cn" ? /* @__PURE__ */ m(Yd, {
			activeIndex: r,
			items: n,
			onItemSelect: i
		}) : /* @__PURE__ */ m(Xd, { value: t })
	});
}
//#endregion
//#region src/components/Views/AlphabetIndexerLable/index.ts
var Qd = /* @__PURE__ */ _({
	AlphabetIndexerLable: () => Zd,
	alphabetIndexerLableTypes: () => qd
}), $d = [
	"Dot",
	"Text",
	"Longest text"
];
function ef({ 类型: e = "Text", count: t, maxCount: n = 99, children: r, className: i, ...a }) {
	let o = tf({
		type: e,
		count: t,
		maxCount: n,
		children: r
	}), s = typeof o == "string" && o.length >= 2;
	return /* @__PURE__ */ m("span", {
		className: X("harmony-badge", `harmony-badge--${e.replace(/\s+/g, "-")}`, e === "Text" && s && "harmony-badge--multi", i),
		role: e === "Dot" ? "status" : void 0,
		"aria-label": e === "Dot" ? void 0 : String(o ?? ""),
		...a,
		children: /* @__PURE__ */ m("span", {
			className: "harmony-badge__text",
			children: o
		})
	});
}
function tf({ type: e, count: t, maxCount: n, children: r }) {
	if (e === "Dot") return null;
	if (r !== void 0) return r;
	if (t === void 0) return null;
	let i = typeof t == "number" ? t : Number(t);
	return Number.isNaN(i) ? t : i > n ? `${n}+` : String(i);
}
//#endregion
//#region src/components/Views/Badge/index.ts
var nf = /* @__PURE__ */ _({
	Badge: () => ef,
	badgeVariants: () => $d
}), rf = "data:image/svg+xml,%3csvg%20viewBox='0%200%20252%20252'%20xmlns='http://www.w3.org/2000/svg'%20xmlns:xlink='http://www.w3.org/1999/xlink'%20width='252.000000'%20height='252.000000'%20fill='none'%20customFrame='%23000000'%3e%3ccircle%20id='椭圆形备份%205'%20cx='126'%20cy='126'%20r='114'%20stroke='rgb(0,0,0)'%20stroke-opacity='0.0470588244'%20stroke-width='24.000000'%20/%3e%3c/svg%3e", af = "data:image/svg+xml,%3csvg%20viewBox='0%200%20128%20128'%20xmlns='http://www.w3.org/2000/svg'%20xmlns:xlink='http://www.w3.org/1999/xlink'%20width='128.000000'%20height='128.000000'%20fill='none'%20customFrame='%23000000'%3e%3ccircle%20id='椭圆形'%20cx='64'%20cy='64'%20r='55'%20stroke='rgb(0,0,0)'%20stroke-opacity='0.0470588244'%20stroke-width='18.000000'%20/%3e%3c/svg%3e", of = "data:image/svg+xml,%3csvg%20viewBox='0%200%2084%2084'%20xmlns='http://www.w3.org/2000/svg'%20xmlns:xlink='http://www.w3.org/1999/xlink'%20width='84.000000'%20height='84.000000'%20fill='none'%20customFrame='%23000000'%3e%3ccircle%20id='椭圆形'%20cx='42'%20cy='42'%20r='35'%20fill='rgb(216,216,216)'%20fill-opacity='0'%20/%3e%3ccircle%20id='椭圆形'%20cx='42'%20cy='42'%20r='35'%20stroke='rgb(0,0,0)'%20stroke-opacity='0.0509803928'%20stroke-width='14.000000'%20/%3e%3c/svg%3e", sf = "data:image/svg+xml;base64,PHN2ZyB2aWV3Qm94PSIwIDAgMjc4LjU3NyAyNzkuMTgiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyIgeG1sbnM6eGxpbms9Imh0dHA6Ly93d3cudzMub3JnLzE5OTkveGxpbmsiIHdpZHRoPSIyNzguNTc3MDI2IiBoZWlnaHQ9IjI3OS4xODAxNzYiIGZpbGw9Im5vbmUiIGN1c3RvbUZyYW1lPSIjMDAwMDAwIj4KCTxkZWZzPgoJCTxnIGlkPSJwaXhzb19jdXN0b21fZWZmZWN0XzQwIj4KCQkJPGVmZmVjdCB2aXNpYmlsaXR5PSJ2aXNpYmxlIiBlZmZlY3RUeXBlPSJnYXVzc2lhbkJsdXIiIHN0ZERldmlhdGlvbj0iMTMuNTkwMDAwMiIgLz4KCQk8L2c+CgkJPGZpbHRlciBpZD0iZmlsdGVyXzQwIiB3aWR0aD0iMjc4LjU3NzAyNiIgaGVpZ2h0PSIyNzkuMTgwMTc2IiB4PSIwLjAwMDAwMCIgeT0iMC4wMDAwMDAiIGZpbHRlclVuaXRzPSJ1c2VyU3BhY2VPblVzZSIgY3VzdG9tRWZmZWN0PSJ1cmwoI3BpeHNvX2N1c3RvbV9lZmZlY3RfNDApIiBjb2xvci1pbnRlcnBvbGF0aW9uLWZpbHRlcnM9InNSR0IiPgoJCQk8ZmVGbG9vZCBmbG9vZC1vcGFjaXR5PSIwIiByZXN1bHQ9IkJhY2tncm91bmRJbWFnZUZpeCIgLz4KCQkJPGZlQmxlbmQgcmVzdWx0PSJzaGFwZSIgaW49IlNvdXJjZUdyYXBoaWMiIGluMj0iQmFja2dyb3VuZEltYWdlRml4IiBtb2RlPSJub3JtYWwiIC8+CgkJCTxmZUdhdXNzaWFuQmx1ciBzdGREZXZpYXRpb249IjQuNTMwMDAwMjEiIHJlc3VsdD0iZWZmZWN0X2xheWVyQmx1cl8xIiAvPgoJCTwvZmlsdGVyPgoJCTxsaW5lYXJHcmFkaWVudCBpZD0icGFpbnRfY3VzdG9tX2dyYWRpZW50XzE1Ij4KCQkJPHN0b3Agc3RvcC1jb2xvcj0icmdiKDI0NSwxMDQsNjEpIiBvZmZzZXQ9IjAuMzM0NjkzMzEzIiBzdG9wLW9wYWNpdHk9IjAuNDAwMDAwMDA2IiAvPgoJCQk8c3RvcCBzdG9wLWNvbG9yPSJyZ2IoMjMwLDExNSwxNjQpIiBvZmZzZXQ9IjAuNDI4OTIyNjUzIiBzdG9wLW9wYWNpdHk9IjAuNDAwMDAwMDA2IiAvPgoJCQk8c3RvcCBzdG9wLWNvbG9yPSJyZ2IoMTgyLDEwNywyMzcpIiBvZmZzZXQ9IjAuNDc4Nzk2NjYxIiBzdG9wLW9wYWNpdHk9IjAuNDAwMDAwMDA2IiAvPgoJCQk8c3RvcCBzdG9wLWNvbG9yPSJyZ2IoMjU1LDE3NSw1NikiIG9mZnNldD0iMSIgc3RvcC1vcGFjaXR5PSIwLjQwMDAwMDAwNiIgLz4KCQk8L2xpbmVhckdyYWRpZW50PgoJCTxtYXNrIGlkPSJvdXRsaW5lX21hc2tfNTEiPgoJCQk8cGF0aCBkPSJNMzcuNDc2MSAxNDkuNjUxQzM4LjEwMDEgMTU2LjAzNCAzOS4zMTI1IDE2Mi4yODggNDEuMTEzMyAxNjguNDE0QzQyLjg3NTUgMTc0LjQwOCA0NS4xNzU4IDE4MC4xOTUgNDguMDE0IDE4NS43NzNDNTAuODEzMyAxOTEuMjc1IDU0LjA5MDkgMTk2LjQ4NyA1Ny44NDY4IDIwMS40MDhDNjEuNTgwNSAyMDYuMzAxIDY1LjcyMjQgMjEwLjgyMiA3MC4yNzI3IDIxNC45NzJDNzQuODMyMiAyMTkuMTMxIDc5LjcyMTkgMjIyLjg0NSA4NC45NDE3IDIyNi4xMTNDOTAuMjEzOCAyMjkuNDE0IDk1LjczNCAyMzIuMjA1IDEwMS41MDIgMjM0LjQ4NUMxMDcuMzc0IDIzNi44MDcgMTEzLjQxMyAyMzguNTY0IDExOS42MTggMjM5Ljc1NkMxMjUuOTg1IDI0MC45NzkgMTMyLjQ0MSAyNDEuNTkgMTM4Ljk4NyAyNDEuNTlDMTQ1Ljk0OCAyNDEuNTkgMTUyLjgwNCAyNDAuODk5IDE1OS41NTYgMjM5LjUxOEMxNjYuMTMgMjM4LjE3MiAxNzIuNTA3IDIzNi4xOTMgMTc4LjY4NiAyMzMuNTc5QzE4NC43NTYgMjMxLjAxMiAxOTAuNTMgMjI3Ljg3OCAxOTYuMDA4IDIyNC4xNzdDMjAxLjQzNyAyMjAuNTA5IDIwNi40NzIgMjE2LjM1NSAyMTEuMTEyIDIxMS43MTVDMjE1Ljc1MiAyMDcuMDc1IDIxOS45MDYgMjAyLjA0IDIyMy41NzQgMTk2LjYxMUMyMjcuMjc1IDE5MS4xMzMgMjMwLjQwOSAxODUuMzU5IDIzMi45NzYgMTc5LjI4OUMyMzUuNTkgMTczLjExIDIzNy41NjkgMTY2LjczMyAyMzguOTE1IDE2MC4xNTlDMjQwLjI5NiAxNTMuNDA3IDI0MC45ODcgMTQ2LjU1MSAyNDAuOTg3IDEzOS41OUMyNDAuOTg3IDEzMi42MjkgMjQwLjI5NiAxMjUuNzczIDIzOC45MTUgMTE5LjAyMUMyMzcuNTY5IDExMi40NDcgMjM1LjU5IDEwNi4wNyAyMzIuOTc2IDk5Ljg5MDhDMjMwLjQwOSA5My44MjExIDIyNy4yNzUgODguMDQ3MyAyMjMuNTc0IDgyLjU2OTNDMjE5LjkwNiA3Ny4xNDAyIDIxNS43NTIgNzIuMTA1NSAyMTEuMTEyIDY3LjQ2NTJDMjA2LjQ3MiA2Mi44MjQ4IDIwMS40MzcgNTguNjcwNyAxOTYuMDA4IDU1LjAwM0MxOTAuNTMgNTEuMzAyMSAxODQuNzU2IDQ4LjE2ODEgMTc4LjY4NiA0NS42MDA4QzE3Mi41MDcgNDIuOTg3MiAxNjYuMTMgNDEuMDA3OCAxNTkuNTU2IDM5LjY2MjVDMTUyLjgwNCAzOC4yODA5IDE0NS45NDggMzcuNTkwMSAxMzguOTg3IDM3LjU5MDFMMTM4Ljk4NyAxMy41OTAxQzE0Ny41NjggMTMuNTkwMSAxNTYuMDI4IDE0LjQ0MzMgMTY0LjM2OCAxNi4xNDk4QzE3Mi41MDEgMTcuODE0MSAxODAuMzkgMjAuMjYzMSAxODguMDM2IDIzLjQ5NjdDMTk1LjUzOSAyNi42NzA1IDIwMi42NzUgMzAuNTQzNiAyMDkuNDQzIDM1LjExNkMyMTYuMTQ0IDM5LjY0MjkgMjIyLjM1NyA0NC43NjkxIDIyOC4wODIgNTAuNDk0NkMyMzMuODA4IDU2LjIyMDIgMjM4LjkzNCA2Mi40MzMzIDI0My40NjEgNjkuMTMzOUMyNDguMDM0IDc1LjkwMiAyNTEuOTA3IDgzLjAzNzkgMjU1LjA4IDkwLjU0MTVDMjU4LjMxNCA5OC4xODY3IDI2MC43NjMgMTA2LjA3NiAyNjIuNDI3IDExNC4yMDlDMjY0LjEzNCAxMjIuNTQ5IDI2NC45ODcgMTMxLjAwOSAyNjQuOTg3IDEzOS41OUMyNjQuOTg3IDE0OC4xNzEgMjY0LjEzNCAxNTYuNjMxIDI2Mi40MjcgMTY0Ljk3MUMyNjAuNzYzIDE3My4xMDQgMjU4LjMxNCAxODAuOTk0IDI1NS4wOCAxODguNjM5QzI1MS45MDcgMTk2LjE0MiAyNDguMDM0IDIwMy4yNzggMjQzLjQ2MSAyMTAuMDQ2QzIzOC45MzQgMjE2Ljc0NyAyMzMuODA4IDIyMi45NiAyMjguMDgyIDIyOC42ODZDMjIyLjM1NyAyMzQuNDExIDIxNi4xNDQgMjM5LjUzNyAyMDkuNDQzIDI0NC4wNjRDMjAyLjY3NSAyNDguNjM3IDE5NS41MzkgMjUyLjUxIDE4OC4wMzYgMjU1LjY4M0MxODAuMzkgMjU4LjkxNyAxNzIuNTAxIDI2MS4zNjYgMTY0LjM2OCAyNjMuMDNDMTU2LjAyOCAyNjQuNzM3IDE0Ny41NjggMjY1LjU5IDEzOC45ODcgMjY1LjU5QzEzMC45MTggMjY1LjU5IDEyMi45NTMgMjY0LjgzNSAxMTUuMDkxIDI2My4zMjVDMTA3LjQxNCAyNjEuODUgOTkuOTQzMiAyNTkuNjc3IDkyLjY3NzkgMjU2LjgwNEM4NS41NDUzIDI1My45ODQgNzguNzIxMSAyNTAuNTM0IDcyLjIwNTUgMjQ2LjQ1NUM2NS43NjEzIDI0Mi40MiA1OS43MjU4IDIzNy44MzYgNTQuMDk5MSAyMzIuNzA0QzQ4LjQ4NTQgMjI3LjU4NCA0My4zNzUgMjIyLjAwNSAzOC43NjggMjE1Ljk2OUMzNC4xMzAyIDIwOS44OTIgMzAuMDgyMSAyMDMuNDU0IDI2LjYyMzUgMTk2LjY1N0MyMy4xMTMxIDE4OS43NTcgMjAuMjY3OCAxODIuNTk5IDE4LjA4NzYgMTc1LjE4M0MxNS44NjA0IDE2Ny42MDYgMTQuMzYxMiAxNTkuODc0IDEzLjU5IDE1MS45ODdMMzcuNDc2MSAxNDkuNjUxWiIgZmlsbD0icmdiKDI1NSwyNTUsMjU1KSIgZmlsbC1ydWxlPSJub256ZXJvIiAvPgoJCTwvbWFzaz4KCTwvZGVmcz4KCTxnIGZpbHRlcj0idXJsKCNmaWx0ZXJfNDApIj4KCQk8cGF0aCBpZD0i6Lev5b6EIiBkPSJNMjUuNTMzMSAxNTAuODE5QzMxLjE3MzQgMjA4LjUwOSA3OS44MTU2IDI1My41OSAxMzguOTg3IDI1My41OUMyMDEuOTQ3IDI1My41OSAyNTIuOTg3IDIwMi41NTEgMjUyLjk4NyAxMzkuNTlDMjUyLjk4NyA3Ni42Mjk2IDIwMS45NDcgMjUuNTkwMSAxMzguOTg3IDI1LjU5MDEiIGZpbGwtcnVsZT0iZXZlbm9kZCIgc3Ryb2tlPSJyZ2IoMCwwLDApIiBzdHJva2Utb3BhY2l0eT0iMCIgc3Ryb2tlLXdpZHRoPSIyNC4wMDAwMDAiIGN1c3RvbUdyYWRpZW50PSJ1cmwoI2N1c3RvbV9ncmFkaWVudF8xNSkiIC8+CgkJPGcgaWQ9ImN1c3RvbV9ncmFkaWVudF8xNSIgYW5ndWxhckdyYWRpZW50PSJ1cmwoI3BhaW50X2N1c3RvbV9ncmFkaWVudF8xNSk7IDExMy43MjY5NzQgMjI3LjcyNzAwNSAxMTMuNzI2OTc0IDExNC4wMDAwMjMgMjI3LjQ1Mzk0OSAxMTQuMDAwMDIzIiBtYXNrPSJ1cmwoI291dGxpbmVfbWFza181MSkiPgoJCQk8Zz4KCQkJCTxmb3JlaWduT2JqZWN0IHdpZHRoPSIyNTEuMzk3MDM0IiBoZWlnaHQ9IjI1Mi4wMDAwMTUiIHg9IjEzLjU4OTk5NiIgeT0iMTMuNTkwMDczIj4KCQkJCQk8ZGl2IHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8xOTk5L3hodG1sIiBzdHlsZT0iYmFja2dyb3VuZDpjb25pYy1ncmFkaWVudChmcm9tIDIxMC40ODk1OTRkZWcgYXQgMTI1LjY3MDAyOXB4IDEyNi4wMDAwNDZweCwgcmdiKDI0NSwxMDQsNjEpIDAlLCByZ2IoMjMwLDExNSwxNjQpIDkuNDIyOTMlLCByZ2IoMTgyLDEwNywyMzcpIDE0LjQxMDMlLCByZ2IoMjU1LDE3NSw1NikgNjYuNTMwNyUsIHJnYigyNDUsMTA0LDYxKSAxMDAlKTttYXNrOmNvbmljLWdyYWRpZW50KGZyb20gMjEwLjQ4OTU5NGRlZyBhdCAxMjUuNjcwMDI5cHggMTI2LjAwMDA0NnB4LCByZ2JhKDI1NSwyNTUsMjU1LDAuNCkgMCUsIHJnYmEoMjU1LDI1NSwyNTUsMC40KSA5LjQyMjkzJSwgcmdiYSgyNTUsMjU1LDI1NSwwLjQpIDE0LjQxMDMlLCByZ2JhKDI1NSwyNTUsMjU1LDAuNCkgNjYuNTMwNyUsIHJnYmEoMjU1LDI1NSwyNTUsMC40KSAxMDAlKTt3aWR0aDoxMDAlO2hlaWdodDoxMDAlOyIgLz4KCQkJCTwvZm9yZWlnbk9iamVjdD4KCQkJPC9nPgoJCTwvZz4KCTwvZz4KPC9zdmc+Cg==", cf = "data:image/svg+xml,%3csvg%20viewBox='0%200%2032.1472%2054.895'%20xmlns='http://www.w3.org/2000/svg'%20xmlns:xlink='http://www.w3.org/1999/xlink'%20width='32.147156'%20height='54.895020'%20fill='none'%20customFrame='%23000000'%3e%3cdefs%3e%3clinearGradient%20id='paint_linear_90'%20x1='20.1168251'%20x2='12.0044975'%20y1='42.8646736'%20y2='9.92444992'%20gradientUnits='userSpaceOnUse'%3e%3cstop%20stop-color='rgb(174,139,224)'%20offset='0'%20stop-opacity='1'%20/%3e%3cstop%20stop-color='rgb(182,107,237)'%20offset='1'%20stop-opacity='1'%20/%3e%3c/linearGradient%3e%3c/defs%3e%3cpath%20id='路径'%20d='M12.0045%2012.0046C13.2656%2022.8266%2016.0423%2033.1859%2020.1168%2042.8647'%20stroke='url(%23paint_linear_90)'%20stroke-linecap='round'%20stroke-linejoin='round'%20stroke-width='24.000000'%20/%3e%3c/svg%3e", lf = "data:image/svg+xml,%3csvg%20viewBox='0%200%2044.9991%2056.9556'%20xmlns='http://www.w3.org/2000/svg'%20xmlns:xlink='http://www.w3.org/1999/xlink'%20width='44.999130'%20height='56.955566'%20fill='none'%20customFrame='%23000000'%3e%3cdefs%3e%3clinearGradient%20id='paint_linear_89'%20x1='32.9503288'%20x2='10.0852127'%20y1='44.9067078'%20y2='7.97018051'%20gradientUnits='userSpaceOnUse'%3e%3cstop%20stop-color='rgb(237,142,184)'%20offset='0'%20stop-opacity='1'%20/%3e%3cstop%20stop-color='rgb(230,115,164)'%20offset='1'%20stop-opacity='1'%20/%3e%3c/linearGradient%3e%3c/defs%3e%3cpath%20id='路径'%20d='M12.03%2012.03C17.0985%2024.1995%2024.2155%2035.3019%2032.9503%2044.9067'%20stroke='url(%23paint_linear_89)'%20stroke-linecap='round'%20stroke-linejoin='round'%20stroke-width='24.000000'%20/%3e%3c/svg%3e", uf = "data:image/svg+xml,%3csvg%20viewBox='0%200%20109.68%2062.7922'%20xmlns='http://www.w3.org/2000/svg'%20xmlns:xlink='http://www.w3.org/1999/xlink'%20width='109.680450'%20height='62.792236'%20fill='none'%20customFrame='%23000000'%3e%3cdefs%3e%3clinearGradient%20id='paint_linear_88'%20x1='97.6805038'%20x2='12.0485611'%20y1='50.7922974'%20y2='12.0485687'%20gradientUnits='userSpaceOnUse'%3e%3cstop%20stop-color='rgb(248,152,123)'%20offset='0'%20stop-opacity='1'%20/%3e%3cstop%20stop-color='rgb(245,104,61)'%20offset='1'%20stop-opacity='1'%20/%3e%3c/linearGradient%3e%3c/defs%3e%3cpath%20id='路径'%20d='M12.0486%2012.0486C32.9406%2035.8023%2063.56%2050.7923%2097.6805%2050.7923'%20stroke='url(%23paint_linear_88)'%20stroke-linecap='round'%20stroke-linejoin='round'%20stroke-width='24.000000'%20/%3e%3c/svg%3e", df = "data:image/svg+xml,%3csvg%20viewBox='0%200%20138%20138'%20xmlns='http://www.w3.org/2000/svg'%20xmlns:xlink='http://www.w3.org/1999/xlink'%20width='138.000000'%20height='138.000000'%20fill='none'%20customFrame='%23000000'%3e%3cdefs%3e%3clinearGradient%20id='paint_linear_92'%20x1='11.9999847'%20x2='11.9999847'%20y1='-102.689941'%20y2='125.999985'%20gradientUnits='userSpaceOnUse'%3e%3cstop%20stop-color='rgb(250,212,25)'%20offset='0'%20stop-opacity='1'%20/%3e%3cstop%20stop-color='rgb(255,175,56)'%20offset='1'%20stop-opacity='1'%20/%3e%3c/linearGradient%3e%3c/defs%3e%3cpath%20id='路径'%20d='M12%20126C74.9605%20126%20126%2074.9605%20126%2012'%20stroke='url(%23paint_linear_92)'%20stroke-linecap='round'%20stroke-linejoin='round'%20stroke-width='24.000000'%20/%3e%3c/svg%3e", ff = "data:image/svg+xml,%3csvg%20viewBox='0%200%20138%20138'%20xmlns='http://www.w3.org/2000/svg'%20xmlns:xlink='http://www.w3.org/1999/xlink'%20width='138.000000'%20height='138.000000'%20fill='none'%20customFrame='%23000000'%3e%3cdefs%3e%3clinearGradient%20id='paint_linear_91'%20x1='12'%20x2='12'%20y1='12'%20y2='240.095505'%20gradientUnits='userSpaceOnUse'%3e%3cstop%20stop-color='rgb(250,212,25)'%20offset='0'%20stop-opacity='1'%20/%3e%3cstop%20stop-color='rgb(255,175,56)'%20offset='1'%20stop-opacity='1'%20/%3e%3c/linearGradient%3e%3c/defs%3e%3cpath%20id='路径'%20d='M126%20126C126%2063.0395%2074.9605%2012%2012%2012'%20stroke='url(%23paint_linear_91)'%20stroke-linecap='round'%20stroke-linejoin='round'%20stroke-width='24.000000'%20/%3e%3c/svg%3e", pf = "data:image/svg+xml,%3csvg%20viewBox='0%200%2021.94%2032.9148'%20xmlns='http://www.w3.org/2000/svg'%20xmlns:xlink='http://www.w3.org/1999/xlink'%20width='21.939972'%20height='32.914795'%20fill='none'%20customFrame='%23000000'%3e%3cdefs%3e%3clinearGradient%20id='paint_linear_87'%20x1='12.9172354'%20x2='9.00338268'%20y1='23.8920326'%20y2='7.9998188'%20gradientUnits='userSpaceOnUse'%3e%3cstop%20stop-color='rgb(174,139,224)'%20offset='0'%20stop-opacity='1'%20/%3e%3cstop%20stop-color='rgb(182,107,237)'%20offset='1'%20stop-opacity='1'%20/%3e%3c/linearGradient%3e%3c/defs%3e%3cpath%20id='路径'%20d='M9.00339%209.00342C9.61181%2014.2245%2010.9515%2019.2225%2012.9172%2023.892'%20stroke='url(%23paint_linear_87)'%20stroke-linecap='round'%20stroke-linejoin='round'%20stroke-width='18.000000'%20/%3e%3c/svg%3e", mf = "data:image/svg+xml,%3csvg%20viewBox='0%200%2028.1523%2033.9207'%20xmlns='http://www.w3.org/2000/svg'%20xmlns:xlink='http://www.w3.org/1999/xlink'%20width='28.152252'%20height='33.920654'%20fill='none'%20customFrame='%23000000'%3e%3cdefs%3e%3clinearGradient%20id='paint_linear_85'%20x1='19.1156425'%20x2='8.08422565'%20y1='24.8840141'%20y2='7.06375504'%20gradientUnits='userSpaceOnUse'%3e%3cstop%20stop-color='rgb(237,142,184)'%20offset='0'%20stop-opacity='1'%20/%3e%3cstop%20stop-color='rgb(230,115,164)'%20offset='1'%20stop-opacity='1'%20/%3e%3c/linearGradient%3e%3c/defs%3e%3cpath%20id='路径'%20d='M9.02249%209.02246C11.4678%2014.8937%2014.9015%2020.2501%2019.1156%2024.884'%20stroke='url(%23paint_linear_85)'%20stroke-linecap='round'%20stroke-linejoin='round'%20stroke-width='18.000000'%20/%3e%3c/svg%3e", hf = "data:image/svg+xml,%3csvg%20viewBox='0%200%2059.3501%2036.7285'%20xmlns='http://www.w3.org/2000/svg'%20xmlns:xlink='http://www.w3.org/1999/xlink'%20width='59.350067'%20height='36.728516'%20fill='none'%20customFrame='%23000000'%3e%3cdefs%3e%3clinearGradient%20id='paint_linear_86'%20x1='50.3500443'%20x2='9.03640366'%20y1='27.7285271'%20y2='9.03637695'%20gradientUnits='userSpaceOnUse'%3e%3cstop%20stop-color='rgb(248,152,123)'%20offset='0'%20stop-opacity='1'%20/%3e%3cstop%20stop-color='rgb(245,104,61)'%20offset='1'%20stop-opacity='1'%20/%3e%3c/linearGradient%3e%3c/defs%3e%3cpath%20id='路径'%20d='M9.03641%209.03638C19.1159%2020.4965%2033.8884%2027.7285%2050.3501%2027.7285'%20stroke='url(%23paint_linear_86)'%20stroke-linecap='round'%20stroke-linejoin='round'%20stroke-width='18.000000'%20/%3e%3c/svg%3e", gf = "data:image/svg+xml,%3csvg%20viewBox='0%200%2073%2073'%20xmlns='http://www.w3.org/2000/svg'%20xmlns:xlink='http://www.w3.org/1999/xlink'%20width='73.000000'%20height='73.000000'%20fill='none'%20customFrame='%23000000'%3e%3cdefs%3e%3clinearGradient%20id='paint_linear_84'%20x1='8.99999237'%20x2='8.99999237'%20y1='-46.3328667'%20y2='63.9999962'%20gradientUnits='userSpaceOnUse'%3e%3cstop%20stop-color='rgb(250,212,25)'%20offset='0'%20stop-opacity='1'%20/%3e%3cstop%20stop-color='rgb(255,175,56)'%20offset='1'%20stop-opacity='1'%20/%3e%3c/linearGradient%3e%3c/defs%3e%3cpath%20id='路径'%20d='M9%2064C39.3757%2064%2064%2039.3757%2064%209'%20stroke='url(%23paint_linear_84)'%20stroke-linecap='round'%20stroke-linejoin='round'%20stroke-width='18.000000'%20/%3e%3c/svg%3e", _f = "data:image/svg+xml,%3csvg%20viewBox='0%200%2073%2073'%20xmlns='http://www.w3.org/2000/svg'%20xmlns:xlink='http://www.w3.org/1999/xlink'%20width='73.000000'%20height='73.000000'%20fill='none'%20customFrame='%23000000'%3e%3cdefs%3e%3clinearGradient%20id='paint_linear_83'%20x1='9'%20x2='9'%20y1='9'%20y2='119.046082'%20gradientUnits='userSpaceOnUse'%3e%3cstop%20stop-color='rgb(250,212,25)'%20offset='0'%20stop-opacity='1'%20/%3e%3cstop%20stop-color='rgb(255,175,56)'%20offset='1'%20stop-opacity='1'%20/%3e%3c/linearGradient%3e%3c/defs%3e%3cpath%20id='路径'%20d='M64%2064C64%2033.6243%2039.3757%209%209%209'%20stroke='url(%23paint_linear_83)'%20stroke-linecap='round'%20stroke-linejoin='round'%20stroke-width='18.000000'%20/%3e%3c/svg%3e", vf = "data:image/svg+xml,%3csvg%20viewBox='0%200%2016.5109%2023.4949'%20xmlns='http://www.w3.org/2000/svg'%20xmlns:xlink='http://www.w3.org/1999/xlink'%20width='16.510925'%20height='23.494873'%20fill='none'%20customFrame='%23000000'%3e%3cdefs%3e%3clinearGradient%20id='paint_linear_80'%20x1='9.49325562'%20x2='7.00261974'%20y1='16.4772587'%20y2='6.36403179'%20gradientUnits='userSpaceOnUse'%3e%3cstop%20stop-color='rgb(174,139,224)'%20offset='0'%20stop-opacity='1'%20/%3e%3cstop%20stop-color='rgb(182,107,237)'%20offset='1'%20stop-opacity='1'%20/%3e%3c/linearGradient%3e%3c/defs%3e%3cpath%20id='路径'%20d='M7.00262%207.00269C7.3898%2010.3252%208.24231%2013.5057%209.49325%2016.4773'%20stroke='url(%23paint_linear_80)'%20stroke-linecap='round'%20stroke-linejoin='round'%20stroke-width='14.000000'%20/%3e%3c/svg%3e", yf = "data:image/svg+xml,%3csvg%20viewBox='0%200%2020.4689%2024.1396'%20xmlns='http://www.w3.org/2000/svg'%20xmlns:xlink='http://www.w3.org/1999/xlink'%20width='20.468872'%20height='24.139648'%20fill='none'%20customFrame='%23000000'%3e%3cdefs%3e%3clinearGradient%20id='paint_linear_81'%20x1='13.4404316'%20x2='6.42044115'%20y1='17.1110497'%20y2='5.77088642'%20gradientUnits='userSpaceOnUse'%3e%3cstop%20stop-color='rgb(237,142,184)'%20offset='0'%20stop-opacity='1'%20/%3e%3cstop%20stop-color='rgb(230,115,164)'%20offset='1'%20stop-opacity='1'%20/%3e%3c/linearGradient%3e%3c/defs%3e%3cpath%20id='路径'%20d='M7.01752%207.01733C8.57364%2010.7536%2010.7587%2014.1622%2013.4404%2017.111'%20stroke='url(%23paint_linear_81)'%20stroke-linecap='round'%20stroke-linejoin='round'%20stroke-width='14.000000'%20/%3e%3c/svg%3e", bf = "data:image/svg+xml,%3csvg%20viewBox='0%200%2040.3188%2025.9233'%20xmlns='http://www.w3.org/2000/svg'%20xmlns:xlink='http://www.w3.org/1999/xlink'%20width='40.318848'%20height='25.923340'%20fill='none'%20customFrame='%23000000'%3e%3cdefs%3e%3clinearGradient%20id='paint_linear_79'%20x1='33.3188248'%20x2='7.02831841'%20y1='18.9233265'%20y2='7.02831745'%20gradientUnits='userSpaceOnUse'%3e%3cstop%20stop-color='rgb(248,152,123)'%20offset='0'%20stop-opacity='1'%20/%3e%3cstop%20stop-color='rgb(245,104,61)'%20offset='1'%20stop-opacity='1'%20/%3e%3c/linearGradient%3e%3c/defs%3e%3cpath%20id='路径'%20d='M7.02832%207.02832C13.4425%2014.3211%2022.8432%2018.9233%2033.3188%2018.9233'%20stroke='url(%23paint_linear_79)'%20stroke-linecap='round'%20stroke-linejoin='round'%20stroke-width='14.000000'%20/%3e%3c/svg%3e", xf = "data:image/svg+xml,%3csvg%20viewBox='0%200%2049%2049'%20xmlns='http://www.w3.org/2000/svg'%20xmlns:xlink='http://www.w3.org/1999/xlink'%20width='49.000000'%20height='49.000000'%20fill='none'%20customFrame='%23000000'%3e%3cdefs%3e%3clinearGradient%20id='paint_linear_78'%20x1='7'%20x2='7'%20y1='-28.2118263'%20y2='41.9999962'%20gradientUnits='userSpaceOnUse'%3e%3cstop%20stop-color='rgb(250,212,25)'%20offset='0'%20stop-opacity='1'%20/%3e%3cstop%20stop-color='rgb(255,175,56)'%20offset='1'%20stop-opacity='1'%20/%3e%3c/linearGradient%3e%3c/defs%3e%3cpath%20id='路径'%20d='M7%2042C26.33%2042%2042%2026.33%2042%207'%20stroke='url(%23paint_linear_78)'%20stroke-linecap='round'%20stroke-linejoin='round'%20stroke-width='14.000000'%20/%3e%3c/svg%3e", Sf = "data:image/svg+xml,%3csvg%20viewBox='0%200%2049%2049'%20xmlns='http://www.w3.org/2000/svg'%20xmlns:xlink='http://www.w3.org/1999/xlink'%20width='49.000000'%20height='49.000000'%20fill='none'%20customFrame='%23000000'%3e%3cdefs%3e%3clinearGradient%20id='paint_linear_82'%20x1='7'%20x2='7'%20y1='7'%20y2='77.0293198'%20gradientUnits='userSpaceOnUse'%3e%3cstop%20stop-color='rgb(250,212,25)'%20offset='0'%20stop-opacity='1'%20/%3e%3cstop%20stop-color='rgb(255,175,56)'%20offset='1'%20stop-opacity='1'%20/%3e%3c/linearGradient%3e%3c/defs%3e%3cpath%20id='路径'%20d='M42%2042C42%2022.67%2026.33%207%207%207'%20stroke='url(%23paint_linear_82)'%20stroke-linecap='round'%20stroke-linejoin='round'%20stroke-width='14.000000'%20/%3e%3c/svg%3e", Cf = [
	"Large",
	"Medium",
	"Small"
], wf = {
	Large: {
		frame: {
			width: 288,
			height: 288
		},
		circle: {
			left: 30,
			top: 30,
			width: 252,
			height: 252
		},
		layers: [
			{
				src: rf,
				style: {
					left: 0,
					top: 0,
					width: 252,
					height: 252
				}
			},
			{
				src: sf,
				style: {
					left: 5,
					top: 5,
					width: 227.4539794921875,
					height: 228,
					overflow: "visible",
					filter: "blur(14px)"
				},
				innerStyle: {
					inset: "-11.223722759046053% -11.238107811772965% -11.223722759046053% -11.238107811772965%",
					opacity: 1,
					WebkitMaskImage: "radial-gradient(circle at center, transparent 50%, black 100%)",
					maskImage: "radial-gradient(circle at center, transparent 50%, black 100%)"
				}
			},
			{
				src: cf,
				style: {
					left: .77197265625,
					top: 127.337646484375,
					width: 32.14715576171875,
					height: 54.89501953125
				}
			},
			{
				src: lf,
				style: {
					left: 8.7177734375,
					top: 157.79931640625,
					width: 44.99913024902344,
					height: 56.95556640625
				}
			},
			{
				src: uf,
				style: {
					left: 28.3681640625,
					top: 189.25634765625,
					width: 109.68045043945312,
					height: 62.792236328125
				}
			},
			{
				src: df,
				style: {
					left: 114,
					top: 114,
					width: 138,
					height: 138
				}
			},
			{
				src: ff,
				style: {
					left: 114,
					top: 0,
					width: 138,
					height: 138
				}
			}
		],
		value: { style: {
			fontSize: 60,
			lineHeight: "80px"
		} },
		percent: { style: {
			fontSize: 16,
			lineHeight: "22px",
			bottom: "9px"
		} },
		subtitle: { style: {
			width: 180,
			fontSize: 14,
			lineHeight: "20px"
		} },
		contentGap: 1,
		percentOffsetY: 3
	},
	Medium: {
		frame: {
			width: 136,
			height: 136
		},
		circle: {
			left: 13,
			top: 13,
			width: 128,
			height: 128
		},
		layers: [
			{
				src: af,
				style: {
					left: 0,
					top: 0,
					width: 128,
					height: 128
				}
			},
			{
				src: pf,
				style: {
					left: 0,
					top: 61.434814453125,
					width: 21.939971923828125,
					height: 32.914794921875
				}
			},
			{
				src: mf,
				style: {
					left: 3.8330078125,
					top: 76.13134765625,
					width: 28.152252197265625,
					height: 33.920654296875
				}
			},
			{
				src: hf,
				style: {
					left: 13.3134765625,
					top: 91.307861328125,
					width: 59.350067138671875,
					height: 36.728515625
				}
			},
			{
				src: gf,
				style: {
					left: 54.6279296875,
					top: 55,
					width: 73,
					height: 73
				}
			},
			{
				src: _f,
				style: {
					left: 54.6279296875,
					top: 0,
					width: 73,
					height: 73
				}
			}
		],
		value: { style: {
			fontSize: 36,
			lineHeight: "48px"
		} },
		percent: { style: {
			fontSize: 16,
			lineHeight: "22px"
		} },
		contentGap: 0,
		percentOffsetY: 0
	},
	Small: {
		frame: {
			width: 88,
			height: 88
		},
		circle: {
			left: 9,
			top: 9,
			width: 84,
			height: 84
		},
		layers: [
			{
				src: of,
				style: {
					left: 0,
					top: 0,
					width: 84,
					height: 84
				}
			},
			{
				src: vf,
				style: {
					left: 0,
					top: 39.094970703125,
					width: 16.51092529296875,
					height: 23.494873046875
				}
			},
			{
				src: yf,
				style: {
					left: 2.439453125,
					top: 48.447265625,
					width: 20.4688720703125,
					height: 24.1396484375
				}
			},
			{
				src: bf,
				style: {
					left: 8.472412109375,
					top: 58.10498046875,
					width: 40.31884765625,
					height: 25.92333984375
				}
			},
			{
				src: xf,
				style: {
					left: 34.7626953125,
					top: 35,
					width: 49,
					height: 49
				}
			},
			{
				src: Sf,
				style: {
					left: 34.7626953125,
					top: 0,
					width: 49,
					height: 49
				}
			}
		]
	}
};
//#endregion
//#region src/components/Views/DataPanelLinearGradient/data-panel-linear-gradient.tsx
function Tf({ 尺寸: e = "Large", 进度: t = 75, 副标题: n = "Used 98GB / 128GB", className: r, ...i }) {
	let a = wf[e], o = a.value && a.percent, s = !!a.subtitle, c = typeof t == "number" ? `${Math.round(t)}` : t ?? "75", l = Ef(a.circle.left), u = Ef(a.circle.top), d = Ef(a.circle.width), f = Ef(a.circle.height);
	return /* @__PURE__ */ h("div", {
		className: X("hm-dp-linear-gradient", `hm-dp-linear-gradient--${e.toLowerCase()}`, r),
		style: {
			width: a.frame.width,
			height: a.frame.height
		},
		...i,
		children: [/* @__PURE__ */ m("div", {
			className: "hm-dp-linear-gradient__circle",
			style: a.circle,
			children: a.layers.map((e, t) => e.innerStyle ? /* @__PURE__ */ m("div", {
				"aria-hidden": "true",
				className: "hm-dp-linear-gradient__layer",
				style: e.style,
				children: /* @__PURE__ */ m("div", {
					className: "hm-dp-linear-gradient__layer-asset",
					style: {
						...e.innerStyle,
						backgroundImage: `url(${e.src})`
					}
				})
			}, `${e.src}-${t}`) : /* @__PURE__ */ m("img", {
				alt: "",
				"aria-hidden": "true",
				className: "hm-dp-linear-gradient__layer hm-dp-linear-gradient__layer-image",
				src: e.src,
				style: e.style
			}, `${e.src}-${t}`))
		}), o ? /* @__PURE__ */ h("div", {
			className: "hm-dp-linear-gradient__content",
			style: {
				gap: a.contentGap ?? 0,
				left: l + d / 2,
				top: u + f / 2,
				width: d
			},
			children: [/* @__PURE__ */ m("div", {
				className: "hm-dp-linear-gradient__value-row",
				children: /* @__PURE__ */ h("p", {
					className: "hm-dp-linear-gradient__value",
					style: {
						...a.value?.style,
						position: "relative"
					},
					children: [c, /* @__PURE__ */ m("span", {
						className: "hm-dp-linear-gradient__percent",
						style: a.percent?.style,
						children: "%"
					})]
				})
			}), s ? /* @__PURE__ */ m("p", {
				className: "hm-dp-linear-gradient__subtitle",
				style: a.subtitle?.style,
				children: n
			}) : null]
		}) : null]
	});
}
function Ef(e) {
	return typeof e == "number" ? e : typeof e == "string" && Number.parseFloat(e) || 0;
}
//#endregion
//#region src/components/Views/DataPanelLinearGradient/index.ts
var Df = /* @__PURE__ */ _({
	DataPanelLinearGradient: () => Tf,
	dpLinearGradientSizes: () => Cf,
	dpLinearGradientVisualMap: () => wf
}), Of = {
	Small: {
		container: 88,
		trackR: 35,
		strokeWidth: 14
	},
	Medium: {
		container: 136,
		trackR: 55,
		strokeWidth: 18
	},
	Large: {
		container: 288,
		trackR: 114,
		strokeWidth: 24
	}
};
function kf({ 尺寸: e = "Large", 进度: t = 50, 版本: n = "5.0.0", className: r, style: i, ...a }) {
	let o = Of[e], s = 2 * Math.PI * o.trackR, c = Math.max(0, Math.min(100, t)), l = s * (1 - c / 100), u = o.container / 2;
	return /* @__PURE__ */ h("div", {
		className: X("hm-datapanel-loading", `hm-datapanel-loading--${e}`, r),
		style: {
			"--dl-circumference": `${s}px`,
			"--dl-dashoffset": `${l}px`,
			...i
		},
		...a,
		children: [
			/* @__PURE__ */ h("svg", {
				viewBox: `0 0 ${o.container} ${o.container}`,
				width: o.container,
				height: o.container,
				children: [
					/* @__PURE__ */ m("defs", { children: /* @__PURE__ */ h("linearGradient", {
						id: "hm-datapanel-loading-gradient",
						x1: "0%",
						y1: "50%",
						x2: "50%",
						y2: "0%",
						children: [
							/* @__PURE__ */ m("stop", {
								offset: "0%",
								stopColor: "rgba(37, 79, 247, 1)"
							}),
							/* @__PURE__ */ m("stop", {
								offset: "20%",
								stopColor: "rgba(37, 79, 247, 0.85)"
							}),
							/* @__PURE__ */ m("stop", {
								offset: "60%",
								stopColor: "rgba(134, 193, 255, 0.15)"
							}),
							/* @__PURE__ */ m("stop", {
								offset: "100%",
								stopColor: "rgba(134, 193, 255, 0)"
							})
						]
					}) }),
					/* @__PURE__ */ m("circle", {
						className: "hm-datapanel-loading__track",
						cx: u,
						cy: u,
						r: o.trackR,
						strokeWidth: o.strokeWidth
					}),
					/* @__PURE__ */ m("circle", {
						className: "hm-datapanel-loading__progress",
						cx: u,
						cy: u,
						r: o.trackR,
						strokeWidth: o.strokeWidth,
						stroke: "url(#hm-datapanel-loading-gradient)",
						strokeDasharray: s,
						strokeDashoffset: l,
						transform: `rotate(-90 ${u} ${u})`
					})
				]
			}),
			e === "Medium" && /* @__PURE__ */ m("div", {
				className: "hm-datapanel-loading__center",
				children: /* @__PURE__ */ h("span", {
					className: "hm-datapanel-loading__value",
					children: [/* @__PURE__ */ m("span", {
						className: "hm-datapanel-loading__num",
						children: c
					}), /* @__PURE__ */ m("span", {
						className: "hm-datapanel-loading__suffix",
						children: "%"
					})]
				})
			}),
			e === "Large" && /* @__PURE__ */ h("div", {
				className: "hm-datapanel-loading__center",
				children: [/* @__PURE__ */ m("span", {
					className: "hm-datapanel-loading__logo",
					children: "HarmonyOS"
				}), /* @__PURE__ */ m("span", {
					className: "hm-datapanel-loading__version",
					children: n
				})]
			})
		]
	});
}
//#endregion
//#region src/components/Views/DataPanelLoading/index.ts
var Af = /* @__PURE__ */ _({ DataPanelLoading: () => kf }), jf = [
	"Large",
	"Medium",
	"Small"
], Mf = {
	Large: 288,
	Medium: 136,
	Small: 88
}, Nf = {
	Large: 114,
	Medium: 55,
	Small: 35
}, Pf = {
	Large: 24,
	Medium: 18,
	Small: 14
}, Ff = {
	Large: 56,
	Medium: 36,
	Small: 0
}, If = {
	Large: 74,
	Medium: 48,
	Small: 0
}, Lf = 13.59;
//#endregion
//#region src/components/Views/DataPanelProgressCircle/data-panel-progress-circle.tsx
function Rf({ 尺寸: e = "Large", 进度: t = 30, 版本: n = "1.0.0", className: r, ...i }) {
	let a = Mf[e], o = Nf[e], s = Pf[e], c = 2 * Math.PI * o, l = c * (1 - Math.min(Math.max(t, 0), 100) / 100), u = Ff[e], d = If[e], f = e !== "Small", p = e === "Large";
	return /* @__PURE__ */ h("div", {
		className: X("hm-dp-progress-circle", `hm-dp-progress-circle--${e}`, r),
		...i,
		children: [/* @__PURE__ */ h("svg", {
			className: "hm-dp-progress-circle__svg",
			viewBox: `0 0 ${a} ${a}`,
			width: a,
			height: a,
			fill: "none",
			xmlns: "http://www.w3.org/2000/svg",
			children: [
				/* @__PURE__ */ m("defs", { children: /* @__PURE__ */ h("linearGradient", {
					id: `dp-progress-grad-${e}`,
					x1: "0%",
					y1: "100%",
					x2: "100%",
					y2: "0%",
					gradientUnits: "objectBoundingBox",
					children: [/* @__PURE__ */ m("stop", {
						offset: "0%",
						stopColor: "#254FF7"
					}), /* @__PURE__ */ m("stop", {
						offset: "100%",
						stopColor: "#86C1FF"
					})]
				}) }),
				e === "Large" && /* @__PURE__ */ m("circle", {
					className: "hm-dp-progress-circle__shadow",
					cx: a / 2,
					cy: a / 2,
					r: o,
					strokeWidth: s,
					stroke: `url(#dp-progress-grad-${e})`,
					strokeLinecap: "round",
					strokeDasharray: c,
					strokeDashoffset: l,
					transform: `rotate(-90 ${a / 2} ${a / 2})`,
					style: { "--dp-shadow-blur": "13.59px" }
				}),
				/* @__PURE__ */ m("circle", {
					className: "hm-dp-progress-circle__track",
					cx: a / 2,
					cy: a / 2,
					r: o,
					strokeWidth: s
				}),
				/* @__PURE__ */ m("circle", {
					className: "hm-dp-progress-circle__fill",
					cx: a / 2,
					cy: a / 2,
					r: o,
					strokeWidth: s,
					stroke: `url(#dp-progress-grad-${e})`,
					strokeLinecap: "round",
					strokeDasharray: c,
					strokeDashoffset: l,
					transform: `rotate(-90 ${a / 2} ${a / 2})`
				})
			]
		}), f && /* @__PURE__ */ h("div", {
			className: "hm-dp-progress-circle__content",
			children: [/* @__PURE__ */ h("div", {
				className: "hm-dp-progress-circle__value-row",
				children: [/* @__PURE__ */ m("span", {
					className: "hm-dp-progress-circle__num",
					style: {
						"--dp-value-font-size": `${u}px`,
						"--dp-value-line-height": `${d}px`
					},
					children: t
				}), /* @__PURE__ */ m("span", {
					className: "hm-dp-progress-circle__percent",
					children: "%"
				})]
			}), p && /* @__PURE__ */ m("span", {
				className: "hm-dp-progress-circle__version",
				children: n
			})]
		})]
	});
}
//#endregion
//#region src/components/Views/DataPanelProgressCircle/index.ts
var zf = /* @__PURE__ */ _({
	DataPanelProgressCircle: () => Rf,
	dpProgressCircleRadiusMap: () => Nf,
	dpProgressCircleShadowBlurLarge: () => Lf,
	dpProgressCircleSizeMap: () => Mf,
	dpProgressCircleSizes: () => jf,
	dpProgressCircleStrokeMap: () => Pf,
	dpProgressCircleValueFontSizeMap: () => Ff,
	dpProgressCircleValueLineHeightMap: () => If
}), Bf = ["Latin", "cn"], Vf = [
	"标准",
	"强",
	"降档",
	"弱"
], Hf = [
	{
		text: "G",
		状态: "activated"
	},
	{
		text: "古",
		状态: "enabled"
	},
	{
		text: "顾",
		状态: "enabled"
	}
];
function Uf({ activeIndex: e, items: t, onItemSelect: n }) {
	return /* @__PURE__ */ m("div", {
		className: "hm-floating-alphabet-indexer-lable__cn-panel",
		children: t.map((t, r) => {
			let i = e === void 0 ? t.状态 === "activated" : r === e;
			return /* @__PURE__ */ m("button", {
				"aria-pressed": i,
				className: X("hm-floating-alphabet-indexer-lable__cn-item", i && "hm-floating-alphabet-indexer-lable__cn-item--activated"),
				onClick: () => n?.(t, r),
				type: "button",
				children: /* @__PURE__ */ m("span", {
					className: "hm-floating-alphabet-indexer-lable__text",
					children: t.text
				})
			}, `${t.text}-${r}`);
		})
	});
}
function Wf({ value: e }) {
	return /* @__PURE__ */ m("div", {
		className: "hm-floating-alphabet-indexer-lable__latin-chip",
		children: /* @__PURE__ */ m("span", {
			className: "hm-floating-alphabet-indexer-lable__text",
			children: e
		})
	});
}
function Gf({ 类型: e = "Latin", 通透度: t = "标准", value: n = "G", items: r = Hf, activeIndex: i, onItemSelect: a, className: o, ...s }) {
	return /* @__PURE__ */ h("div", {
		className: X("hm-floating-alphabet-indexer-lable", "hm-material-style-layer-floating-ultra-thick-effect-1", `hm-floating-alphabet-indexer-lable--type-${e.toLowerCase()}`, `hm-floating-alphabet-indexer-lable--opacity-${Kf(t)}`, o),
		"data-type": e,
		"data-opacity": t,
		...s,
		children: [
			/* @__PURE__ */ m("div", { className: "hm-material-style-layer hm-material-style-layer-floating-ultra-thick-fill-1" }),
			/* @__PURE__ */ m("div", { className: "hm-material-style-layer hm-material-style-layer-floating-ultra-thick-effect-2" }),
			/* @__PURE__ */ m("div", { className: "hm-material-style-layer hm-material-style-layer-floating-ultra-thick-effect-3" }),
			/* @__PURE__ */ m("div", { className: "hm-material-style-layer hm-material-style-layer-floating-ultra-thick-effect-4" }),
			/* @__PURE__ */ m("div", { className: "hm-material-style-layer hm-material-style-layer-floating-ultra-thick-effect-5" }),
			/* @__PURE__ */ m("div", { className: "hm-material-style-layer hm-material-style-layer-floating-ultra-thick-effect-6" }),
			/* @__PURE__ */ m("div", { className: "hm-material-style-layer hm-material-style-layer-floating-ultra-thick-effect-7" }),
			/* @__PURE__ */ m("div", { className: "hm-material-style-layer hm-material-style-layer-floating-ultra-thick-effect-8" }),
			e === "cn" ? /* @__PURE__ */ m(Uf, {
				activeIndex: i,
				items: r,
				onItemSelect: a
			}) : /* @__PURE__ */ m(Wf, { value: n })
		]
	});
}
function Kf(e) {
	switch (e) {
		case "标准": return "standard";
		case "强": return "strong";
		case "降档": return "downgraded";
		case "弱": return "weak";
	}
}
//#endregion
//#region src/components/Views/FloatingAlphabetIndexerLable/index.ts
var qf = /* @__PURE__ */ _({
	FloatingAlphabetIndexerLable: () => Gf,
	floatingAlphabetIndexerLableOpacities: () => Vf,
	floatingAlphabetIndexerLableTypes: () => Bf
}), Jf = [
	"Text",
	"multiline text",
	"Full pattern"
], Yf = [
	"标准",
	"强",
	"降档",
	"弱"
], Xf = "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA", Zf = "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA", Qf = "Title", $f = "Text button", ep = { fontFamily: "HarmonyHeiTi, HarmonyHeiTi-Regular, var(--font-sans)" }, tp = { fontFamily: "HarmonyHeiTi, HarmonyHeiTi-Medium, var(--font-sans)" };
function np({ className: e }) {
	return /* @__PURE__ */ m(Z, {
		className: X("hm-floating-popup-tip__close-icon", e),
		name: "xmark",
		size: 18
	});
}
function rp({ children: e, className: t }) {
	return /* @__PURE__ */ m("p", {
		className: X("hm-floating-popup-tip__link", t),
		style: tp,
		children: e
	});
}
function ip() {
	return /* @__PURE__ */ h("div", {
		"aria-hidden": "true",
		className: "hm-floating-popup-tip__arrow hm-material-style-layer-floating-thick-effect-1",
		children: [
			/* @__PURE__ */ m("div", { className: "hm-material-style-layer hm-material-style-layer-floating-thick-fill-1" }),
			/* @__PURE__ */ m("div", { className: "hm-material-style-layer hm-material-style-layer-floating-thick-fill-2" }),
			/* @__PURE__ */ m("div", { className: "hm-material-style-layer hm-material-style-layer-floating-thick-effect-2" }),
			/* @__PURE__ */ m("div", { className: "hm-material-style-layer hm-material-style-layer-floating-thick-effect-3" }),
			/* @__PURE__ */ m("div", { className: "hm-material-style-layer hm-material-style-layer-floating-thick-effect-4" }),
			/* @__PURE__ */ m("div", { className: "hm-material-style-layer hm-material-style-layer-floating-thick-effect-5" }),
			/* @__PURE__ */ m("div", { className: "hm-material-style-layer hm-material-style-layer-floating-thick-effect-6" }),
			/* @__PURE__ */ m("div", { className: "hm-material-style-layer hm-material-style-layer-floating-thick-effect-7" }),
			/* @__PURE__ */ m("div", { className: "hm-material-style-layer hm-material-style-layer-floating-thick-effect-8" })
		]
	});
}
function ap({ 类型: e = "Text", 通透度: t = "标准", close: n = !0, image: r = !0, Link: i = !0, title: a, description: o, linkText1: s = $f, linkText2: c = $f, imageSrc: l, onClose: u, className: d, ...f }) {
	let p = e === "Text", g = e === "multiline text", _ = e === "Full pattern", v = a ?? (_ ? Qf : Xf), y = o ?? Zf, b = l ?? "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAqgAAAKoCAIAAAA02poLAAAAAXNSR0IArs4c6QAAAERlWElmTU0AKgAAAAgAAYdpAAQAAAABAAAAGgAAAAAAA6ABAAMAAAABAAEAAKACAAQAAAABAAACqKADAAQAAAABAAACqAAAAAA5kNdeAABAAElEQVR4Ae3dBYBUVdvAcUW6QZBQupFeQmBhQVCRkO4OpaS7u3dZWlAEBQmlu2MBQaVBQlIQUEJCGkG/B3k/xM2Jc+7c+KMv7s7c+5zn/M6888zcOOell/iDAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIImFPgZXOmRVa6BW7dvqupiVQpkt+7d09TcDOHjRs37q+Xr2rKMFGCeJoiux5W1WvmyZMnASX8Dx8+5HrTbOmNQOLEiX/YszdFipTeBHm2rxleh973ggjRIEAAAQSMFHjllVcmTZkifxvZqJPbGjZ8hJKq72RDm/Wdwm+zAaU7CFhAIF++/O07dLRAotZPsWTJgAYNG1m/H/RApQCFX6UmsRBAwEWBnr16Z8qUycWN2cwzgThx4kyYNNmzfdnLxgIUfhsPLl1DwLwCsWPHlpr08stcZqRxjPr1H5AhQwaNDRDamgIUfmuOG1kjYH0Bf/8STZs1s34/TNqDAgUKtG7T1qTJkZZPBSj8PuWncQScLTBo8NBUqVI520BL76NHjz5x8pRo0XiH18Jr9aC8LKw+guSPgIUFEiZMGDR2nIU7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AAF1AhR+dZZEQgABBBBAwPQCFH7TDxEJIoAAAgggoE6Awq/OkkgIIIAAAgiYXoDCb/ohIkEEEEAAAQTUCVD41VkSCQEEEEAAAdMLUPhNP0QkiAACCCCAgDoBCr86SyIhgAACCCBgegEKv+mHiAQRQAABBBBQJ0DhV2dJJAQQQAABBEwvQOE3/RCRIAIIIIAAAuoEKPzqLImEAAIIIICA6QUo/KYfIhJEAAEEEEBAnQCFX50lkRBAAAEEEDC9AIXf9ENEgggggAACCKgToPCrsyQSAggggAACpheg8Jt+iEgQAQQQQAABdQIUfnWWREIAAQQQQMD0AhR+0w8RCSKAAAIIIKBOgMKvzpJICCCAAAIImF6Awm/6ISJBBBBAAAEE1AlQ+NVZEgkBBBBAAAHTC1D4TT9EJIgAAggggIA6AQq/OksiIYAAAgggYHoBCr/ph4gEEUAAAQQQUCdA4VdnSSQEEEAAAQRML0DhN/0QkSACCCCAAALqBCj86iyJhAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAqEEXg71O78iYGaBWLFiZcqUOUvWLFmyZE2ZKlWC+PInwf/+efrjPw/Ej//nn3/euXP79u078rf88/Tnf/66devW2bNnTp44efLkiV9//dXMPSU3gwVefvnluHHjxosnL6N48vezf+LEjfPnn48fPXz48On/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42XhOGMbpzU1AnJfSZEib8nrqnTpt/PkzSvL/6iJ63KUo0ePbJf78UO2frtjh0xw6fJ+bIiAXgEKv15forsrIHcBFPDzCwgoVTIgQN61jbxrS+Ye+KfSP633ly5dcjdztjezgHwIePPNN2VuiXz58svfWbJk1fH58tq1q6dPnT5yROp9yLbt21igwcwvCSfnRuF38uibve9yAaBM2JI9e3Z5m5a7AeVvOTWg6vTtnTt3TskVVidPyl+y0MCBA/tlnl2zi5CfOgGZBzBjpowZMmSUP6lSpUqWLPmrr8qNAsnkf4kSJQq3HTliLyfp796V185d+e/tP26fP3/utPw5dUr+J68fuUo/3B15EAFTCVD4TTUcJBOFgBwAyJQps3wMkA8BKVOlSiCLAsVP8L9/nv74zwPx48uJ+Tt35FyqvEHfln+e/ixv1XfuyPvymTOnT56Qcn+Ca/KjsHb203JeQF5scpwgZsxYMWJEv//ggRR8qfrOVqH3CCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIKBI4GVFcQhjZ4FXYr/6RtNrdu6h7/p29/iMa1ua+659WkYAAccJRHNcj+kwAggggAACDhag8Dt48Ok6AggggIDzBCj8zhtzeowAAggg4GABCr+DB5+uI4AAAgg4T4DC77wxp8cIIIAAAg4WoPA7ePDpOgIIIICA8wQo/M4bc3qMAAIIIOBgAQq/gwefriOAAAIIOE+Awu+8MafHCCCAAAIOFqDwO3jw6ToCCCCAgPMEKPzOG3N6jAACCCDgYAEKv4MHn64jgAACCDhPgMLvvDGnxwgggAACDhag8Dt48Ok6AggggIDzBCj8zhtzeowAAggg4GABCr+DB5+uI4AAAgg4T4DC77wxp8cIIIAAAg4WoPA7ePDpOgIIIICA8wQo/M4bc3qMAAIIIOBgAQq/gwefriOAAAIIOE+Awu+8MafHCCCAAAIOFqDwO3jw6ToCCCCAgPMEKPzOG3N6jAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACCCCAAAIIIIAAAggggAACDhf4P2d81mxy6mkDAAAAAElFTkSuQmCC";
	return /* @__PURE__ */ h("div", {
		className: X("hm-floating-popup-tip", "hm-material-style-layer-floating-thick-effect-1", d),
		"data-类型": e,
		"data-通透度": t,
		...f,
		children: [
			/* @__PURE__ */ m(ip, {}),
			/* @__PURE__ */ m("div", { className: "hm-material-style-layer hm-material-style-layer-floating-thick-fill-1" }),
			/* @__PURE__ */ m("div", { className: "hm-material-style-layer hm-material-style-layer-floating-thick-fill-2" }),
			/* @__PURE__ */ m("div", { className: "hm-material-style-layer hm-material-style-layer-floating-thick-effect-2" }),
			/* @__PURE__ */ m("div", { className: "hm-material-style-layer hm-material-style-layer-floating-thick-effect-3" }),
			/* @__PURE__ */ m("div", { className: "hm-material-style-layer hm-material-style-layer-floating-thick-effect-4" }),
			/* @__PURE__ */ m("div", { className: "hm-material-style-layer hm-material-style-layer-floating-thick-effect-5" }),
			/* @__PURE__ */ m("div", { className: "hm-material-style-layer hm-material-style-layer-floating-thick-effect-6" }),
			/* @__PURE__ */ m("div", { className: "hm-material-style-layer hm-material-style-layer-floating-thick-effect-7" }),
			/* @__PURE__ */ m("div", { className: "hm-material-style-layer hm-material-style-layer-floating-thick-effect-8" }),
			_ && r ? /* @__PURE__ */ m("div", {
				"aria-hidden": "true",
				className: "hm-floating-popup-tip__image",
				style: { backgroundImage: `url(${b})` }
			}) : null,
			/* @__PURE__ */ h("div", {
				className: "hm-floating-popup-tip__content",
				children: [
					/* @__PURE__ */ h("div", {
						className: "hm-floating-popup-tip__primary-row",
						children: [_ ? /* @__PURE__ */ m("p", {
							className: "hm-floating-popup-tip__title",
							style: tp,
							children: v
						}) : g ? /* @__PURE__ */ m("p", {
							className: "hm-floating-popup-tip__text hm-floating-popup-tip__text--multiline",
							style: ep,
							children: y
						}) : /* @__PURE__ */ m("p", {
							className: "hm-floating-popup-tip__text hm-floating-popup-tip__text--single",
							style: ep,
							children: v
						}), n ? /* @__PURE__ */ m("button", {
							"aria-label": "关闭",
							className: X("hm-floating-popup-tip__close", p && "hm-floating-popup-tip__close--text"),
							onClick: u,
							type: "button",
							children: /* @__PURE__ */ m(np, {})
						}) : null]
					}),
					_ ? /* @__PURE__ */ m("p", {
						className: "hm-floating-popup-tip__text hm-floating-popup-tip__text--multiline",
						style: ep,
						children: y
					}) : null,
					(g || _) && i ? /* @__PURE__ */ h("div", {
						className: "hm-floating-popup-tip__links",
						children: [/* @__PURE__ */ m(rp, { children: s }), /* @__PURE__ */ m(rp, { children: c })]
					}) : null
				]
			})
		]
	});
}
//#endregion
//#region src/components/Views/FloatingPopupTip/index.ts
var op = /* @__PURE__ */ _({
	CloseIcon: () => np,
	FloatingPopupTip: () => ap,
	FloatingPopupTipArrow: () => ip,
	TextLink: () => rp,
	floatingPopupTipTransparencies: () => Yf,
	floatingPopupTipTypes: () => Jf
}), sp = ["1", "2"], cp = [
	"button+arrow",
	"smallbutton+cancel",
	"cancel",
	"text button",
	"text+cancel"
], lp = ["24icon", "image"], up = [
	"Nomal",
	"Hover",
	"Pressed",
	"Disable"
];
//#endregion
//#region src/components/Views/Snackbar/Snackbar.tsx
function dp({ className: e }) {
	return /* @__PURE__ */ m(Z, {
		className: X("snackbar-arrow", e),
		name: "chevron_right",
		size: 24,
		style: {
			fontSize: 18,
			width: 12
		}
	});
}
function fp({ className: e }) {
	return /* @__PURE__ */ m(Z, {
		className: e,
		name: "segmented_button_highlight",
		size: 24
	});
}
function pp({ className: e }) {
	return /* @__PURE__ */ m(Z, {
		className: e,
		name: "xmark",
		size: 32,
		style: { fontSize: 16 }
	});
}
function mp({ 右侧区域: e = "text+cancel", 文字按钮状态: t = "Nomal", 按钮文案: n = "TEXT BT", onAction: r, onClose: i, 关闭按钮无障碍标签: a = "关闭" }) {
	switch (e) {
		case "button+arrow": return /* @__PURE__ */ m("div", {
			className: "snackbar-right snackbar-right--button-arrow",
			children: /* @__PURE__ */ h("button", {
				type: "button",
				className: "snackbar-action-btn",
				onClick: r,
				children: [/* @__PURE__ */ m("span", {
					className: "snackbar-action-text",
					children: n
				}), /* @__PURE__ */ m(dp, {})]
			})
		});
		case "smallbutton+cancel": return /* @__PURE__ */ h("div", {
			className: "snackbar-right snackbar-right--smallbutton-cancel",
			children: [/* @__PURE__ */ m("button", {
				type: "button",
				className: "snackbar-emphasized-btn",
				onClick: r,
				children: n === "TEXT BT" ? "BTN" : n
			}), /* @__PURE__ */ m("button", {
				type: "button",
				"aria-label": a,
				className: "snackbar-close-btn",
				onClick: i,
				children: /* @__PURE__ */ m(pp, {})
			})]
		});
		case "cancel": return /* @__PURE__ */ m("div", {
			className: "snackbar-right snackbar-right--cancel",
			children: /* @__PURE__ */ m("button", {
				type: "button",
				"aria-label": a,
				className: "snackbar-close-btn",
				onClick: i,
				children: /* @__PURE__ */ m(pp, {})
			})
		});
		case "text button": return /* @__PURE__ */ m("div", {
			className: "snackbar-right snackbar-right--text-button",
			children: /* @__PURE__ */ m("button", {
				type: "button",
				className: X("snackbar-text-btn", `snackbar-text-btn--${t}`),
				disabled: t === "Disable",
				onClick: r,
				children: n
			})
		});
		default: return /* @__PURE__ */ h("div", {
			className: "snackbar-right snackbar-right--text-cancel",
			children: [/* @__PURE__ */ m("button", {
				type: "button",
				className: X("snackbar-text-btn", `snackbar-text-btn--${t}`),
				disabled: t === "Disable",
				onClick: r,
				children: n
			}), /* @__PURE__ */ m("button", {
				type: "button",
				"aria-label": a,
				className: "snackbar-close-btn",
				onClick: i,
				children: /* @__PURE__ */ m(pp, {})
			})]
		});
	}
}
function hp({ 左侧区域: e = "1", 左侧图标类型: t = "24icon", 右侧区域: n = "text+cancel", 文字按钮状态: r = "Nomal", 标题: i = "Title", 副标题: a = "Subtitle", 按钮文案: o = "TEXT BT", 图片: s, 图标: c, onAction: l, onClose: u, 关闭按钮无障碍标签: d = "关闭", 底部偏移: f, className: p, ...g }) {
	let _ = /* @__PURE__ */ h("div", {
		"aria-live": "polite",
		className: X("snackbar-root", p),
		"data-left-region": e,
		"data-left-icon-type": t,
		"data-right-region": n,
		role: "status",
		...g,
		children: [/* @__PURE__ */ h("div", {
			className: "snackbar-left",
			children: [t === "image" ? /* @__PURE__ */ m("span", {
				className: "snackbar-image",
				children: s ?? /* @__PURE__ */ m("span", {
					className: "snackbar-image-placeholder",
					"aria-hidden": "true"
				})
			}) : /* @__PURE__ */ m("span", {
				className: "snackbar-icon",
				children: c ?? /* @__PURE__ */ m(fp, {})
			}), e === "1" ? /* @__PURE__ */ m("span", {
				className: "snackbar-title snackbar-title--single",
				children: i
			}) : /* @__PURE__ */ h("div", {
				className: "snackbar-copy",
				children: [/* @__PURE__ */ m("span", {
					className: "snackbar-title",
					children: i
				}), /* @__PURE__ */ m("span", {
					className: "snackbar-subtitle",
					children: a
				})]
			})]
		}), /* @__PURE__ */ m(mp, {
			右侧区域: n,
			文字按钮状态: r,
			按钮文案: o,
			onAction: l,
			onClose: u,
			关闭按钮无障碍标签: d
		})]
	});
	return f === void 0 ? _ : /* @__PURE__ */ m("div", {
		className: "absolute left-0 right-0 flex justify-center",
		style: {
			bottom: `${f}px`,
			zIndex: 60
		},
		children: _
	});
}
//#endregion
//#region src/components/Views/Snackbar/index.ts
var gp = /* @__PURE__ */ _({
	Snackbar: () => hp,
	SnackbarCloseIcon: () => pp,
	snackbarLeftIconTypes: () => lp,
	snackbarLeftRegions: () => sp,
	snackbarRightRegions: () => cp,
	snackbarTextButtonStates: () => up
}), _p = ["1", "2"], vp = [
	"button+arrow",
	"smallbutton+cancel",
	"cancel",
	"text button",
	"text+cancel"
], yp = ["24icon", "image"], bp = [
	"Nomal",
	"Hover",
	"Pressed",
	"Disable"
], xp = [
	"标准",
	"强",
	"降档",
	"弱"
];
//#endregion
//#region src/components/Views/FloatingSnackbar/FloatingSnackbar.tsx
function Sp({ className: e }) {
	return /* @__PURE__ */ m(Z, {
		className: X("hm-floating-snackbar__arrow", e),
		name: "chevron_right",
		size: 24,
		style: {
			fontSize: 18,
			width: 12
		}
	});
}
function Cp({ className: e }) {
	return /* @__PURE__ */ m(Z, {
		className: e,
		name: "segmented_button_highlight",
		size: 24
	});
}
function wp({ 右侧区域: e = "text+cancel", 文字按钮状态: t = "Nomal", 按钮文案: n = "TEXT BT", onAction: r, onClose: i, 关闭按钮无障碍标签: a = "关闭" }) {
	switch (e) {
		case "button+arrow": return /* @__PURE__ */ m("div", {
			className: "hm-floating-snackbar__right hm-floating-snackbar__right--button-arrow",
			children: /* @__PURE__ */ h("button", {
				type: "button",
				className: "hm-floating-snackbar__action-btn",
				onClick: r,
				children: [/* @__PURE__ */ m("span", {
					className: "hm-floating-snackbar__action-text",
					children: n
				}), /* @__PURE__ */ m(Sp, {})]
			})
		});
		case "smallbutton+cancel": return /* @__PURE__ */ h("div", {
			className: "hm-floating-snackbar__right hm-floating-snackbar__right--smallbutton-cancel",
			children: [/* @__PURE__ */ m("button", {
				type: "button",
				className: "hm-floating-snackbar__emphasized-btn",
				onClick: r,
				children: n === "TEXT BT" ? "BTN" : n
			}), /* @__PURE__ */ m("button", {
				type: "button",
				"aria-label": a,
				className: "hm-floating-snackbar__close",
				onClick: i,
				children: /* @__PURE__ */ m(pp, {})
			})]
		});
		case "cancel": return /* @__PURE__ */ m("div", {
			className: "hm-floating-snackbar__right hm-floating-snackbar__right--cancel",
			children: /* @__PURE__ */ m("button", {
				type: "button",
				"aria-label": a,
				className: "hm-floating-snackbar__close",
				onClick: i,
				children: /* @__PURE__ */ m(pp, {})
			})
		});
		case "text button": return /* @__PURE__ */ m("div", {
			className: "hm-floating-snackbar__right hm-floating-snackbar__right--text-button",
			children: /* @__PURE__ */ m("button", {
				type: "button",
				className: X("hm-floating-snackbar__text-btn", `hm-floating-snackbar__text-btn--${t}`),
				disabled: t === "Disable",
				onClick: r,
				children: n
			})
		});
		default: return /* @__PURE__ */ h("div", {
			className: "hm-floating-snackbar__right hm-floating-snackbar__right--text-cancel",
			children: [/* @__PURE__ */ m("button", {
				type: "button",
				className: X("hm-floating-snackbar__text-btn", `hm-floating-snackbar__text-btn--${t}`),
				disabled: t === "Disable",
				onClick: r,
				children: n
			}), /* @__PURE__ */ m("button", {
				type: "button",
				"aria-label": a,
				className: "hm-floating-snackbar__close",
				onClick: i,
				children: /* @__PURE__ */ m(pp, {})
			})]
		});
	}
}
function Tp({ 左侧区域: e = "1", 左侧图标类型: t = "24icon", 右侧区域: n = "text+cancel", 文字按钮状态: r = "Nomal", 通透度: i = "标准", 标题: a = "Title", 副标题: o = "Subtitle", 按钮文案: s = "TEXT BT", 图片: c, 图标: l, onAction: u, onClose: d, 关闭按钮无障碍标签: f = "关闭", className: p, ...g }) {
	return /* @__PURE__ */ h("div", {
		"aria-live": "polite",
		className: X("hm-floating-snackbar", "hm-material-style-layer-floating-thick-effect-1", p),
		"data-left-region": e,
		"data-left-icon-type": t,
		"data-right-region": n,
		"data-transparency": i,
		role: "status",
		...g,
		children: [
			/* @__PURE__ */ m("div", { className: "hm-material-style-layer hm-material-style-layer-floating-thick-fill-1" }),
			/* @__PURE__ */ m("div", { className: "hm-material-style-layer hm-material-style-layer-floating-thick-fill-2" }),
			/* @__PURE__ */ m("div", { className: "hm-material-style-layer hm-material-style-layer-floating-thick-effect-2" }),
			/* @__PURE__ */ m("div", { className: "hm-material-style-layer hm-material-style-layer-floating-thick-effect-3" }),
			/* @__PURE__ */ m("div", { className: "hm-material-style-layer hm-material-style-layer-floating-thick-effect-4" }),
			/* @__PURE__ */ m("div", { className: "hm-material-style-layer hm-material-style-layer-floating-thick-effect-5" }),
			/* @__PURE__ */ m("div", { className: "hm-material-style-layer hm-material-style-layer-floating-thick-effect-6" }),
			/* @__PURE__ */ m("div", { className: "hm-material-style-layer hm-material-style-layer-floating-thick-effect-7" }),
			/* @__PURE__ */ m("div", { className: "hm-material-style-layer hm-material-style-layer-floating-thick-effect-8" }),
			/* @__PURE__ */ h("div", {
				className: "hm-floating-snackbar__left",
				children: [t === "image" ? /* @__PURE__ */ m("span", {
					className: "hm-floating-snackbar__image",
					children: c ?? /* @__PURE__ */ m("span", {
						className: "hm-floating-snackbar__image-placeholder",
						"aria-hidden": "true"
					})
				}) : /* @__PURE__ */ m("span", {
					className: "hm-floating-snackbar__icon",
					children: l ?? /* @__PURE__ */ m(Cp, {})
				}), e === "1" ? /* @__PURE__ */ m("span", {
					className: "hm-floating-snackbar__title hm-floating-snackbar__title--single",
					children: a
				}) : /* @__PURE__ */ h("div", {
					className: "hm-floating-snackbar__copy",
					children: [/* @__PURE__ */ m("span", {
						className: "hm-floating-snackbar__title",
						children: a
					}), /* @__PURE__ */ m("span", {
						className: "hm-floating-snackbar__subtitle",
						children: o
					})]
				})]
			}),
			/* @__PURE__ */ m(wp, {
				右侧区域: n,
				文字按钮状态: r,
				按钮文案: s,
				onAction: u,
				onClose: d,
				关闭按钮无障碍标签: f
			})
		]
	});
}
//#endregion
//#region src/components/Views/FloatingSnackbar/index.ts
var Ep = /* @__PURE__ */ _({
	FloatingSnackbar: () => Tp,
	floatingSnackbarLeftIconTypes: () => yp,
	floatingSnackbarLeftRegions: () => _p,
	floatingSnackbarRightRegions: () => vp,
	floatingSnackbarTextButtonStates: () => bp,
	floatingSnackbarTransparencies: () => xp
}), Dp = [
	"标准",
	"强",
	"降档",
	"弱"
];
//#endregion
//#region src/components/Views/FloatingToast/FloatingToast.tsx
function Op({ 内容: e = "Toast content", 通透度: t = "标准", className: n, ...r }) {
	return /* @__PURE__ */ h("div", {
		"aria-live": "polite",
		className: X("hm-floating-toast", "hm-material-style-layer-floating-thick-effect-1", n),
		"data-transparency": t,
		role: "status",
		...r,
		children: [
			/* @__PURE__ */ m("div", { className: "hm-material-style-layer hm-material-style-layer-floating-thick-fill-1" }),
			/* @__PURE__ */ m("div", { className: "hm-material-style-layer hm-material-style-layer-floating-thick-fill-2" }),
			/* @__PURE__ */ m("div", { className: "hm-material-style-layer hm-material-style-layer-floating-thick-effect-2" }),
			/* @__PURE__ */ m("div", { className: "hm-material-style-layer hm-material-style-layer-floating-thick-effect-3" }),
			/* @__PURE__ */ m("div", { className: "hm-material-style-layer hm-material-style-layer-floating-thick-effect-4" }),
			/* @__PURE__ */ m("div", { className: "hm-material-style-layer hm-material-style-layer-floating-thick-effect-5" }),
			/* @__PURE__ */ m("div", { className: "hm-material-style-layer hm-material-style-layer-floating-thick-effect-6" }),
			/* @__PURE__ */ m("div", { className: "hm-material-style-layer hm-material-style-layer-floating-thick-effect-7" }),
			/* @__PURE__ */ m("div", { className: "hm-material-style-layer hm-material-style-layer-floating-thick-effect-8" }),
			/* @__PURE__ */ m("span", {
				className: "hm-floating-toast__label",
				children: e
			})
		]
	});
}
//#endregion
//#region src/components/Views/FloatingToast/index.ts
var kp = /* @__PURE__ */ _({
	FloatingToast: () => Op,
	floatingToastTransparencies: () => Dp
}), Ap = {
	Large: {
		container: 288,
		radius: 118,
		stroke: 18,
		mainTop: 74,
		defaultMainSize: 56,
		defaultMainLine: 72,
		standardMainSize: 80,
		standardMainLine: 108,
		bottomLabelSize: 30,
		bottomLabelLine: 40,
		bottomLabelBottom: 18,
		bottomRowSize: 48,
		bottomRowLine: 64,
		bottomRowBottom: 16,
		subtitleSize: 16,
		subtitleLine: 24,
		subtitleGap: 2,
		runnerSize: 68,
		runnerBottom: 8,
		arrowSize: 24,
		arrowTop: 42,
		arrowLeft: 34,
		arrowRight: 32
	},
	Small: {
		container: 136,
		radius: 60,
		stroke: 10,
		mainTop: 32,
		defaultMainSize: 48,
		defaultMainLine: 64,
		standardMainSize: 36,
		standardMainLine: 64,
		bottomLabelSize: 26,
		bottomLabelLine: 36,
		bottomLabelBottom: 8,
		bottomRowSize: 20,
		bottomRowLine: 28,
		bottomRowBottom: 7,
		subtitleSize: 14,
		subtitleLine: 20,
		subtitleGap: 0,
		runnerSize: 32,
		runnerBottom: 6,
		arrowSize: 14,
		arrowTop: 18,
		arrowLeft: 13,
		arrowRight: 12
	},
	Mini: {
		container: 88,
		radius: 38,
		stroke: 8,
		mainTop: 20,
		defaultMainSize: 30,
		defaultMainLine: 40,
		standardMainSize: 30,
		standardMainLine: 40,
		bottomLabelSize: 14,
		bottomLabelLine: 20,
		bottomLabelBottom: 4,
		bottomRowSize: 14,
		bottomRowLine: 20,
		bottomRowBottom: 5,
		subtitleSize: 12,
		subtitleLine: 16,
		subtitleGap: 0,
		runnerSize: 24,
		runnerBottom: 2,
		arrowSize: 10,
		arrowTop: 11,
		arrowLeft: 8,
		arrowRight: 7
	}
}, jp = 228, Mp = 492, Np = 10, Pp = 18, Fp = [
	{
		color: "#0A59F7",
		percentage: 21,
		endColor: "#87C2FF",
		gradientStops: [{
			offset: "0%",
			color: "#0A59F7",
			stopOpacity: 1
		}, {
			offset: "100%",
			color: "#87C2FF",
			stopOpacity: .72
		}]
	},
	{
		color: "#48D7DE",
		percentage: 14,
		endColor: "#87D8FF",
		gradientStops: [{
			offset: "0%",
			color: "#48D7DE",
			stopOpacity: 1
		}, {
			offset: "100%",
			color: "#87D8FF",
			stopOpacity: .3
		}]
	},
	{
		color: "#59D14A",
		percentage: 18,
		endColor: "#59D14A",
		gradientStops: [{
			offset: "0%",
			color: "#59D14A",
			stopOpacity: 1
		}, {
			offset: "100%",
			color: "#59D14A",
			stopOpacity: .3
		}]
	},
	{
		color: "#D5F220",
		percentage: 10,
		endColor: "#D5F220",
		gradientStops: [
			{
				offset: "0%",
				color: "#D5F220",
				stopOpacity: 1
			},
			{
				offset: "55.9511065%",
				color: "#D5F220",
				stopOpacity: .41568628
			},
			{
				offset: "100%",
				color: "#D5F220",
				stopOpacity: 0
			}
		]
	},
	{
		color: "#FFC51B",
		percentage: 11,
		endColor: "#FFC51B",
		gradientStops: [
			{
				offset: "0%",
				color: "#FFC51B",
				stopOpacity: 1
			},
			{
				offset: "43.2942301%",
				color: "#FFC51B",
				stopOpacity: .486274511
			},
			{
				offset: "100%",
				color: "#FFC51B",
				stopOpacity: 0
			}
		]
	},
	{
		color: "#FF781B",
		percentage: 8,
		endColor: "#FFB81B",
		gradientStops: [
			{
				offset: "0%",
				color: "#FF781B",
				stopOpacity: 1
			},
			{
				offset: "53.9652407%",
				color: "#FFB81B",
				stopOpacity: .419607848
			},
			{
				offset: "100%",
				color: "#FFC51B",
				stopOpacity: 0
			}
		]
	},
	{
		color: "#FF473A",
		percentage: 18,
		endColor: "#EA493E",
		gradientStops: [
			{
				offset: "0%",
				color: "#EA493E",
				stopOpacity: 1
			},
			{
				offset: "55.5108964%",
				color: "#FF473A",
				stopOpacity: .517647088
			},
			{
				offset: "100%",
				color: "#EA493E",
				stopOpacity: 0
			}
		]
	}
], Ip = [
	{
		color: "#0A59F7",
		percentage: 21,
		gradientStops: [{
			offset: "0%",
			color: "#0A59F7",
			stopOpacity: 1
		}, {
			offset: "100%",
			color: "#87C2FF",
			stopOpacity: .721568627
		}]
	},
	{
		color: "#48D7DE",
		percentage: 14,
		gradientStops: [{
			offset: "0%",
			color: "#48D7DE",
			stopOpacity: 1
		}, {
			offset: "100%",
			color: "#87D8FF",
			stopOpacity: .301960784
		}]
	},
	{
		color: "#59D14A",
		percentage: 18,
		gradientStops: [{
			offset: "0%",
			color: "#59D14A",
			stopOpacity: 1
		}, {
			offset: "100%",
			color: "#59D14A",
			stopOpacity: .301960784
		}]
	},
	{
		color: "#D5F220",
		percentage: 10,
		gradientStops: [
			{
				offset: "0%",
				color: "#D5F220",
				stopOpacity: 1
			},
			{
				offset: "55.9511065%",
				color: "#D5F220",
				stopOpacity: .41568628
			},
			{
				offset: "100%",
				color: "#D5F220",
				stopOpacity: 0
			}
		]
	},
	{
		color: "#FFC51B",
		percentage: 11,
		gradientStops: [
			{
				offset: "0%",
				color: "#FFC51B",
				stopOpacity: 1
			},
			{
				offset: "43.2942301%",
				color: "#FFC51B",
				stopOpacity: .486274511
			},
			{
				offset: "100%",
				color: "#FFC51B",
				stopOpacity: 0
			}
		]
	},
	{
		color: "#FF781B",
		percentage: 8,
		gradientStops: [
			{
				offset: "0%",
				color: "#FF781B",
				stopOpacity: 1
			},
			{
				offset: "58.2156003%",
				color: "#FFB81B",
				stopOpacity: .419607843
			},
			{
				offset: "100%",
				color: "#FFC51B",
				stopOpacity: 0
			}
		]
	},
	{
		color: "#FF473A",
		percentage: 18,
		gradientStops: [
			{
				offset: "0%",
				color: "#EA493E",
				stopOpacity: 1
			},
			{
				offset: "53.8205028%",
				color: "#FF473A",
				stopOpacity: .517647059
			},
			{
				offset: "100%",
				color: "#EA493E",
				stopOpacity: 0
			}
		]
	}
], Lp = [
	{
		offset: "0%",
		color: "#FF4A43"
	},
	{
		offset: "18%",
		color: "#FF7A36"
	},
	{
		offset: "48%",
		color: "#FBD530"
	},
	{
		offset: "100%",
		color: "#44D54F"
	}
], Rp = {
	Large: [
		{
			offset: "0%",
			color: "#44D54F"
		},
		{
			offset: "18%",
			color: "#B9DB26"
		},
		{
			offset: "44%",
			color: "#F7AF1F"
		},
		{
			offset: "74%",
			color: "#F56B31"
		},
		{
			offset: "100%",
			color: "#F0453F"
		}
	],
	Small: [
		{
			offset: "0%",
			color: "#44D54F"
		},
		{
			offset: "18%",
			color: "#B9DB26"
		},
		{
			offset: "44%",
			color: "#F7AF1F"
		},
		{
			offset: "74%",
			color: "#F56B31"
		},
		{
			offset: "100%",
			color: "#F0453F"
		}
	],
	Mini: Lp
}, zp = {
	Default: {
		Large: {
			数值: "22",
			标签: "AQI",
			说明: "已超出正常值范围"
		},
		Small: {
			数值: "22",
			标签: "AQI"
		},
		Mini: {
			数值: "22",
			标签: "AQI"
		}
	},
	Line: {
		Large: {
			数值: "40",
			左值: "18",
			右值: "30"
		},
		Small: {
			数值: "2222",
			左值: "18",
			右值: "30"
		},
		Mini: {
			数值: "22",
			标签: "AQI"
		}
	},
	"Double Data": {
		Large: {
			数值: "40",
			左值: "18",
			右值: "30",
			进度: 86
		},
		Small: {
			数值: "22",
			左值: "18",
			右值: "30",
			进度: 86
		},
		Mini: {
			数值: "22",
			标签: "AQI",
			进度: 86
		}
	},
	Progress: {
		Large: {
			数值: "40",
			进度: 84
		},
		Small: {
			数值: "40",
			进度: 84
		},
		Mini: {
			数值: "40",
			进度: 84
		}
	},
	"Multi Segment": {
		Large: {
			数值: "40",
			标签: "AQI"
		},
		Small: {
			数值: "22",
			标签: "AQI"
		},
		Mini: {
			数值: "22",
			标签: "AQI"
		}
	}
};
function Bp(e, t, n, r) {
	let i = (r - 90) * Math.PI / 180;
	return {
		x: e + n * Math.cos(i),
		y: t + n * Math.sin(i)
	};
}
function Vp(e, t, n, r, i) {
	let a = Bp(e, t, n, i), o = Bp(e, t, n, r), s = i - r <= 180 ? "0" : "1";
	return [
		"M",
		a.x,
		a.y,
		"A",
		n,
		n,
		0,
		s,
		0,
		o.x,
		o.y
	].join(" ");
}
function Hp(e, t) {
	return Math.max(0, Math.min(100, e ?? t));
}
function Up({ size: e, className: t }) {
	return /* @__PURE__ */ h("svg", {
		"aria-hidden": "true",
		className: t,
		viewBox: "0 0 15.0809 12.1196",
		width: e,
		height: e * 12.1196 / 15.0809,
		fill: "none",
		xmlns: "http://www.w3.org/2000/svg",
		children: [/* @__PURE__ */ m("path", {
			d: "M6.2827 2.55904L2.28395 7.87839C1.59029 8.80112 2.24863 10.1196 3.40301 10.1196L11.6776 10.1196C12.853 10.1196 13.5051 8.75866 12.7687 7.84252L8.49295 2.52317C7.92083 1.81141 6.83143 1.82909 6.2827 2.55904Z",
			fill: "rgba(0,0,0,0.898039)",
			fillRule: "evenodd"
		}), /* @__PURE__ */ m("path", {
			d: "M4.68404 1.35726L0.685282 6.67661C0.55145 6.85464 0.436684 7.04195 0.340985 7.23855C0.292567 7.33801 0.249029 7.43985 0.210372 7.54407Q0.125466 7.77298 0.0748653 8.00923L0.0748619 8.00924Q0.025437 8.24001 0.00874329 8.47779Q-0.0219537 8.91502 0.0551218 9.33234L0.0551873 9.3327C0.11251 9.64287 0.214486 9.9448 0.361117 10.2385Q0.581057 10.679 0.901278 11.0273L0.901306 11.0273C1.09287 11.2356 1.31135 11.4192 1.55675 11.5781C1.69018 11.6645 1.8283 11.7407 1.97112 11.8068C2.11725 11.8745 2.2683 11.9316 2.42425 11.978Q2.584 12.0256 2.74684 12.0572Q3.06887 12.1196 3.40301 12.1196L11.6776 12.1196C11.9053 12.1196 12.1288 12.0979 12.348 12.0545C12.4569 12.0329 12.5647 12.0059 12.6714 11.9736Q12.9089 11.9018 13.1309 11.7971L13.1309 11.7971L13.131 11.7971C13.2754 11.729 13.4149 11.6506 13.5495 11.5617C13.7964 11.3987 14.0154 11.2106 14.2066 10.9976C14.4205 10.7593 14.5995 10.4898 14.7437 10.1889C14.8879 9.88807 14.9858 9.57966 15.0375 9.26368L15.0375 9.26365Q15.1069 8.83992 15.0655 8.39805Q15.0429 8.15716 14.9867 7.92437C14.9484 7.76528 14.8983 7.60902 14.8364 7.4556C14.7947 7.35214 14.7482 7.25121 14.6968 7.15282Q14.5416 6.85578 14.3276 6.5895L10.0518 1.27015Q9.78345 0.936329 9.45213 0.685791C9.25543 0.537048 9.04208 0.410321 8.81209 0.305612Q8.47572 0.152476 8.12274 0.0761378C7.8704 0.0215625 7.61168 -0.00357425 7.3466 0.000727415Q6.949 0.0071795 6.57334 0.101274L6.57332 0.101281C6.33977 0.159782 6.11259 0.243689 5.89178 0.353002Q5.55207 0.521174 5.26442 0.753741L5.26423 0.753888Q4.94133 1.015 4.68404 1.35726ZM2.28395 7.87839L6.2827 2.55904C6.83143 1.82909 7.92083 1.81141 8.49295 2.52317L12.7687 7.84252C13.5051 8.75866 12.853 10.1196 11.6776 10.1196L3.40301 10.1196C2.24863 10.1196 1.59029 8.80112 2.28395 7.87839Z",
			fill: "#fff",
			fillRule: "evenodd"
		})]
	});
}
function Wp({ size: e }) {
	return /* @__PURE__ */ h("svg", {
		"aria-hidden": "true",
		viewBox: "0 0 22.5249 24.5317",
		width: e,
		height: e * 24.5317 / 22.5249,
		fill: "none",
		xmlns: "http://www.w3.org/2000/svg",
		children: [/* @__PURE__ */ m("path", {
			d: "M18.1231 2.02021C18.1231 2.99123 17.3313 3.77904 16.3563 3.77904C15.3793 3.77904 14.5874 2.99123 14.5874 2.02021C14.5874 1.04848 15.3793 0.261719 16.3563 0.261719C17.3313 0.261719 18.1231 1.04848 18.1231 2.02021ZM17.6106 16.6074C18.2663 18.7381 18.888 21.5421 19.1928 23.2292L19.2289 23.4319C19.3075 23.8052 19.0625 24.1707 18.6819 24.2475C18.3529 24.3143 18.0293 24.1427 17.898 23.853L17.8271 23.7083C17.3903 22.7958 16.4128 20.5726 15.6993 18.761C15.3908 17.9775 14.9324 17.2605 14.2002 16.7842C12.8519 15.9072 10.4291 14.4589 9.91724 13.9798C9.16768 13.2782 9.0391 12.3429 9.47696 11.4C9.53395 11.2772 10.2227 9.56792 10.6856 8.43807C10.8548 8.36948 11.0098 8.31454 11.1227 8.29099C11.3344 8.24629 11.6544 8.14528 11.9314 8.02243C11.9699 8.00537 12.0071 7.98797 12.0436 7.97022L12.054 7.9651C12.0864 7.94907 12.1176 7.93269 12.1479 7.91631C12.1538 7.91289 12.16 7.90948 12.1659 7.90641C12.1923 7.8914 12.2174 7.87638 12.2417 7.86137C12.2493 7.85659 12.257 7.85181 12.2643 7.84703C12.2855 7.83338 12.3049 7.81939 12.3233 7.8054C12.3313 7.7996 12.3397 7.7938 12.347 7.788C12.3637 7.77469 12.3776 7.76172 12.3915 7.7491C12.3984 7.74227 12.4061 7.73579 12.4123 7.72931C12.4245 7.71668 12.4335 7.7044 12.4429 7.69177C12.4481 7.68494 12.454 7.67812 12.4585 7.67129C12.4665 7.65867 12.471 7.6457 12.4756 7.63308C12.4776 7.62727 12.4815 7.62113 12.4829 7.61499C12.487 7.59656 12.4881 7.57814 12.4839 7.56039C12.4811 7.54776 12.4735 7.5365 12.4617 7.52661C12.453 7.5191 12.4398 7.5133 12.4269 7.5075C12.4224 7.50545 12.4196 7.50272 12.4144 7.50067C12.2962 7.45665 12.0401 7.45563 11.7225 7.47849L11.7225 7.47815C11.2788 7.51023 10.7137 7.58974 10.2307 7.6672L8.97759 7.84703C8.97759 7.84703 6.25248 10.0781 5.73644 10.6681L5.49527 10.9626C5.34341 11.1277 5.09321 11.183 4.87811 11.0823C4.63972 10.9711 4.52539 10.707 4.59906 10.4661L4.6776 10.2603C5.32152 8.88509 7.7179 6.27596 7.7179 6.27596L7.72589 6.27084C7.84821 6.1299 8.00737 6.02344 8.1905 5.96406L8.19884 5.95894C8.19884 5.95894 9.36124 5.57197 12.0255 4.90382C13.0194 4.65472 13.6616 4.55746 13.6616 4.55746L13.6637 4.56019C13.8006 4.53665 13.9406 4.52197 14.0845 4.52197C15.4262 4.52197 16.5156 5.59074 16.5156 6.91033C16.5156 7.35223 16.3909 7.76479 16.1782 8.11969L16.1792 8.12139L13.475 12.4135C13.475 12.4135 16.1851 14.7521 16.8826 15.4502C17.2652 15.8335 17.4653 16.1358 17.6106 16.6074ZM21.7403 10.4977C19.9054 10.4309 17.794 9.99455 17.794 9.99455L16.9966 8.0732C16.9803 8.03378 16.9544 8.00565 16.9478 8.09767C16.9367 8.25457 16.8864 8.53158 16.6965 8.88216C16.3917 9.44451 16.1152 9.75906 15.7925 10.358C15.8193 10.4036 16.2195 11.2853 16.2777 11.3688C16.462 11.6316 16.7605 11.8024 17.1004 11.8117L17.1053 11.8144C17.1053 11.8144 20.0866 11.8661 21.8939 11.5153C22.1078 11.4489 22.2631 11.251 22.2631 11.0173C22.2631 10.7304 22.0292 10.4977 21.7403 10.4977ZM7.51722 15.9257L8.68176 13.9629C8.68176 13.9629 8.95265 14.4109 9.40017 14.7676C9.79359 15.0816 11.0475 15.8165 11.0475 15.8165L9.40332 17.9345C8.8186 18.6228 8.2681 18.7118 7.32837 18.6769C4.06863 18.5546 1.97867 18.3502 1.12656 18.225L0.895114 18.1836C0.585128 18.1533 0.322967 17.9319 0.272 17.6306C0.210911 17.2707 0.47377 16.9329 0.859158 16.8758L1.18939 16.8383C3.16799 16.7099 4.68057 16.6013 6.54502 16.4673C6.9538 16.4376 7.33256 16.2674 7.51722 15.9257Z",
			fill: "#CFFF00"
		}), /* @__PURE__ */ m("path", {
			d: "M18.1231 2.02021C18.1231 2.99123 17.3313 3.77904 16.3563 3.77904C15.3793 3.77904 14.5874 2.99123 14.5874 2.02021C14.5874 1.04848 15.3793 0.261719 16.3563 0.261719C17.3313 0.261719 18.1231 1.04848 18.1231 2.02021ZM17.6106 16.6074C18.2663 18.7381 18.888 21.5421 19.1928 23.2292L19.2289 23.4319C19.3075 23.8052 19.0625 24.1707 18.6819 24.2475C18.3529 24.3143 18.0293 24.1427 17.898 23.853L17.8271 23.7083C17.3903 22.7958 16.4128 20.5726 15.6993 18.761C15.3908 17.9775 14.9324 17.2605 14.2002 16.7842C12.8519 15.9072 10.4291 14.4589 9.91724 13.9798C9.16768 13.2782 9.0391 12.3429 9.47696 11.4C9.53395 11.2772 10.2227 9.56792 10.6856 8.43807C10.8548 8.36948 11.0098 8.31454 11.1227 8.29099C11.3344 8.24629 11.6544 8.14528 11.9314 8.02243C11.9699 8.00537 12.0071 7.98797 12.0436 7.97022L12.054 7.9651C12.0864 7.94907 12.1176 7.93269 12.1479 7.91631C12.1538 7.91289 12.16 7.90948 12.1659 7.90641C12.1923 7.8914 12.2174 7.87638 12.2417 7.86137C12.2493 7.85659 12.257 7.85181 12.2643 7.84703C12.2855 7.83338 12.3049 7.81939 12.3233 7.8054C12.3313 7.7996 12.3397 7.7938 12.347 7.788C12.3637 7.77469 12.3776 7.76172 12.3915 7.7491C12.3984 7.74227 12.4061 7.73579 12.4123 7.72931C12.4245 7.71668 12.4335 7.7044 12.4429 7.69177C12.4481 7.68494 12.454 7.67812 12.4585 7.67129C12.4665 7.65867 12.471 7.6457 12.4756 7.63308C12.4776 7.62727 12.4815 7.62113 12.4829 7.61499C12.487 7.59656 12.4881 7.57814 12.4839 7.56039C12.4811 7.54776 12.4735 7.5365 12.4617 7.52661C12.453 7.5191 12.4398 7.5133 12.4269 7.5075C12.4224 7.50545 12.4196 7.50272 12.4144 7.50067C12.2962 7.45665 12.0401 7.45563 11.7225 7.47849L11.7225 7.47815C11.2788 7.51023 10.7137 7.58974 10.2307 7.6672L8.97759 7.84703C8.97759 7.84703 6.25248 10.0781 5.73644 10.6681L5.49527 10.9626C5.34341 11.1277 5.09321 11.183 4.87811 11.0823C4.63972 10.9711 4.52539 10.707 4.59906 10.4661L4.6776 10.2603C5.32152 8.88509 7.7179 6.27596 7.7179 6.27596L7.72589 6.27084C7.84821 6.1299 8.00737 6.02344 8.1905 5.96406L8.19884 5.95894C8.19884 5.95894 9.36124 5.57197 12.0255 4.90382C13.0194 4.65472 13.6616 4.55746 13.6616 4.55746L13.6637 4.56019C13.8006 4.53665 13.9406 4.52197 14.0845 4.52197C15.4262 4.52197 16.5156 5.59074 16.5156 6.91033C16.5156 7.35223 16.3909 7.76479 16.1782 8.11969L16.1792 8.12139L13.475 12.4135C13.475 12.4135 16.1851 14.7521 16.8826 15.4502C17.2652 15.8335 17.4653 16.1358 17.6106 16.6074ZM21.7403 10.4977C19.9054 10.4309 17.794 9.99455 17.794 9.99455L16.9966 8.0732C16.9803 8.03378 16.9544 8.00565 16.9478 8.09767C16.9367 8.25457 16.8864 8.53158 16.6965 8.88216C16.3917 9.44451 16.1152 9.75906 15.7925 10.358C15.8193 10.4036 16.2195 11.2853 16.2777 11.3688C16.462 11.6316 16.7605 11.8024 17.1004 11.8117L17.1053 11.8144C17.1053 11.8144 20.0866 11.8661 21.8939 11.5153C22.1078 11.4489 22.2631 11.251 22.2631 11.0173C22.2631 10.7304 22.0292 10.4977 21.7403 10.4977ZM7.51722 15.9257L8.68176 13.9629C8.68176 13.9629 8.95265 14.4109 9.40017 14.7676C9.79359 15.0816 11.0475 15.8165 11.0475 15.8165L9.40332 17.9345C8.8186 18.6228 8.2681 18.7118 7.32837 18.6769C4.06863 18.5546 1.97867 18.3502 1.12656 18.225L0.895114 18.1836C0.585128 18.1533 0.322967 17.9319 0.272 17.6306C0.210911 17.2707 0.47377 16.9329 0.859158 16.8758L1.18939 16.8383C3.16799 16.7099 4.68057 16.6013 6.54502 16.4673C6.9538 16.4376 7.33256 16.2674 7.51722 15.9257Z",
			stroke: "#CFFF00",
			strokeWidth: "0.523716"
		})]
	});
}
function Gp({ path: e, stroke: t, strokeWidth: n, dasharray: r, dashoffset: i, opacity: a, linecap: o = "round", filter: s }) {
	return /* @__PURE__ */ m("path", {
		d: e,
		pathLength: 100,
		fill: "none",
		stroke: t,
		strokeWidth: n,
		strokeLinecap: o,
		strokeDasharray: r,
		strokeDashoffset: i,
		opacity: a,
		filter: s
	});
}
var Kp = [
	{
		id: "paint_linear_0",
		x1: 196.296631,
		y1: 252.146332,
		x2: 244.904404,
		y2: 199.322739,
		stops: [
			{
				offset: "0",
				color: "rgb(234,73,62)",
				stopOpacity: 1
			},
			{
				offset: "0.555108964",
				color: "rgb(255,71,58)",
				stopOpacity: .517647088
			},
			{
				offset: "1",
				color: "rgb(234,73,62)",
				stopOpacity: 0
			}
		]
	},
	{
		id: "paint_linear_1",
		x1: 231.11293,
		y1: 199.322769,
		x2: -51.3693848,
		y2: 321.344269,
		stops: [{
			offset: "0",
			color: "rgb(255,255,255)",
			stopOpacity: 0
		}, {
			offset: "1",
			color: "rgb(255,255,255)",
			stopOpacity: 1
		}]
	},
	{
		id: "paint_linear_2",
		x1: 225.415024,
		y1: 222.318848,
		x2: 264.20282,
		y2: 150.727814,
		stops: [
			{
				offset: "0",
				color: "rgb(255,120,27)",
				stopOpacity: 1
			},
			{
				offset: "0.539652407",
				color: "rgb(255,184,27)",
				stopOpacity: .419607848
			},
			{
				offset: "1",
				color: "rgb(255,197,27)",
				stopOpacity: 0
			}
		]
	},
	{
		id: "paint_linear_3",
		x1: 243.550766,
		y1: 201.739227,
		x2: 233.932144,
		y2: 214.12706,
		stops: [{
			offset: "0",
			color: "rgb(255,255,255)",
			stopOpacity: 0
		}, {
			offset: "1",
			color: "rgb(255,255,255)",
			stopOpacity: 1
		}]
	},
	{
		id: "paint_linear_4",
		x1: 268.954865,
		y1: 176.476593,
		x2: 244.550293,
		y2: 66.1128464,
		stops: [
			{
				offset: "0",
				color: "rgb(255,197,27)",
				stopOpacity: 1
			},
			{
				offset: "0.432942301",
				color: "rgb(255,197,27)",
				stopOpacity: .486274511
			},
			{
				offset: "1",
				color: "rgb(255,197,27)",
				stopOpacity: 0
			}
		]
	},
	{
		id: "paint_linear_5",
		x1: 259.895874,
		y1: 167.738556,
		x2: 256.752594,
		y2: 176.476624,
		stops: [{
			offset: "0",
			color: "rgb(255,255,255)",
			stopOpacity: 0
		}, {
			offset: "1",
			color: "rgb(255,255,255)",
			stopOpacity: 1
		}]
	},
	{
		id: "paint_linear_6",
		x1: 264.597961,
		y1: 121.494675,
		x2: 192.668884,
		y2: 27.9036713,
		stops: [
			{
				offset: "0",
				color: "rgb(213,242,32)",
				stopOpacity: 1
			},
			{
				offset: "0.559511065",
				color: "rgb(213,242,32)",
				stopOpacity: .41568628
			},
			{
				offset: "1",
				color: "rgb(213,242,32)",
				stopOpacity: 0
			}
		]
	},
	{
		id: "paint_linear_7",
		x1: 255.881821,
		y1: 111.21772,
		x2: 260.306976,
		y2: 121.494667,
		stops: [{
			offset: "0",
			color: "rgb(255,255,255)",
			stopOpacity: 0
		}, {
			offset: "1",
			color: "rgb(255,255,255)",
			stopOpacity: 1
		}]
	},
	{
		id: "paint_linear_8",
		x1: 225.454895,
		y1: 62.2226868,
		x2: 104.110504,
		y2: 18.631794,
		stops: [{
			offset: "0",
			color: "rgb(89,209,74)",
			stopOpacity: 1
		}, {
			offset: "1",
			color: "rgb(89,209,74)",
			stopOpacity: .301960796
		}]
	},
	{
		id: "paint_linear_9",
		x1: 225.45491,
		y1: 57.4977341,
		x2: 221.923157,
		y2: 55.0544777,
		stops: [{
			offset: "0",
			color: "rgb(255,255,255)",
			stopOpacity: 1
		}, {
			offset: "1",
			color: "rgb(255,255,255)",
			stopOpacity: 0
		}]
	},
	{
		id: "paint_linear_10",
		x1: 26.2078285,
		y1: 153.273804,
		x2: 122.871353,
		y2: 22.5820465,
		stops: [{
			offset: "0",
			color: "rgb(135,216,255)",
			stopOpacity: .301960796
		}, {
			offset: "1",
			color: "rgb(72,215,222)",
			stopOpacity: 1
		}]
	},
	{
		id: "paint_linear_11",
		x1: 122.871292,
		y1: 28.4944859,
		x2: 116.560753,
		y2: 43.8076401,
		stops: [
			{
				offset: "0",
				color: "rgb(255,255,255)",
				stopOpacity: 1
			},
			{
				offset: "0.333134413",
				color: "rgb(255,255,255)",
				stopOpacity: .600000024
			},
			{
				offset: "1",
				color: "rgb(255,255,255)",
				stopOpacity: 0
			}
		]
	},
	{
		id: "paint_linear_12",
		x1: 75.3841476,
		y1: 240.040222,
		x2: 18.9028893,
		y2: 87.267334,
		stops: [{
			offset: "0",
			color: "rgb(135,194,255)",
			stopOpacity: .721568644
		}, {
			offset: "1",
			color: "rgb(10,89,247)",
			stopOpacity: 1
		}]
	},
	{
		id: "paint_linear_13",
		x1: 47.143486,
		y1: 96.9150391,
		x2: 25.6435032,
		y2: 147.535873,
		stops: [{
			offset: "0",
			color: "rgb(255,255,255)",
			stopOpacity: 1
		}, {
			offset: "1",
			color: "rgb(255,255,255)",
			stopOpacity: 0
		}]
	}
], qp = [
	{
		d: "M233.383 203.394C236.106 199.235 241.685 198.071 245.843 200.794C250.001 203.517 251.165 209.096 248.442 213.254C242.494 222.338 235.394 230.617 227.334 237.874C223.641 241.2 217.95 240.902 214.624 237.208C211.298 233.514 211.596 227.824 215.29 224.498C222.198 218.277 228.285 211.18 233.383 203.394Z",
		fill: "paint_linear_0"
	},
	{
		d: "M245.843 200.794C250.001 203.517 251.165 209.096 248.442 213.254C242.494 222.338 235.394 230.617 227.334 237.874C223.641 241.2 217.95 240.902 214.624 237.208C211.298 233.514 211.596 227.824 215.29 224.498C222.198 218.277 228.285 211.18 233.383 203.394C236.106 199.235 241.685 198.071 245.843 200.794Z",
		stroke: "paint_linear_1",
		strokeWidth: 2
	},
	{
		d: "M259.955 135.273C264.926 135.273 268.955 139.303 268.955 144.273C268.955 167.718 262.547 190.238 250.619 209.81C248.032 214.054 242.494 215.398 238.25 212.811C234.005 210.224 232.661 204.686 235.248 200.442C245.468 183.674 250.955 164.391 250.955 144.273C250.955 139.303 254.984 135.273 259.955 135.273Z",
		fill: "paint_linear_2"
	},
	{
		d: "M268.955 144.273C268.955 167.718 262.547 190.238 250.619 209.81C248.032 214.054 242.494 215.398 238.25 212.811C234.005 210.224 232.661 204.686 235.248 200.442C245.468 183.674 250.955 164.391 250.955 144.273C250.955 139.303 254.984 135.273 259.955 135.273C264.926 135.273 268.955 139.303 268.955 144.273Z",
		stroke: "paint_linear_3",
		strokeWidth: 2
	},
	{
		d: "M250.612 97.4608C255.31 95.8367 260.435 98.3284 262.059 103.026C266.606 116.179 268.955 130.072 268.955 144.274C268.955 152.729 268.122 161.083 266.484 169.246C265.505 174.12 260.761 177.277 255.888 176.299C251.015 175.32 247.857 170.577 248.836 165.703C250.241 158.705 250.955 151.538 250.955 144.274C250.955 132.08 248.942 120.175 245.047 108.907C243.423 104.21 245.914 99.0849 250.612 97.4608Z",
		fill: "paint_linear_4"
	},
	{
		d: "M262.059 103.026C266.606 116.179 268.955 130.072 268.955 144.274C268.955 152.729 268.122 161.083 266.484 169.246C265.505 174.12 260.761 177.277 255.888 176.299C251.015 175.32 247.857 170.577 248.836 165.703C250.241 158.705 250.955 151.538 250.955 144.274C250.955 132.08 248.942 120.175 245.047 108.907C243.423 104.21 245.914 99.0849 250.612 97.4608C255.31 95.8367 260.435 98.3284 262.059 103.026Z",
		stroke: "paint_linear_5",
		strokeWidth: 2
	},
	{
		d: "M143.929 18.6318C200.257 18.6318 249.176 56.3874 264.26 110.057C265.605 114.842 262.816 119.812 258.031 121.157C253.246 122.502 248.276 119.713 246.931 114.928C234.012 68.96 192.125 36.6318 143.929 36.6318C138.958 36.6318 134.929 32.6024 134.929 27.6318C134.929 22.6613 138.958 18.6318 143.929 18.6318Z",
		fill: "paint_linear_6"
	},
	{
		d: "M143.929 16.6318Q155.404 16.6318 166.515 18.6441Q175.899 20.3435 185.023 23.4783Q193.965 26.5506 202.264 30.8624L202.264 30.8625Q211.958 35.8998 220.774 42.6285Q229.024 48.9251 236.064 56.3663L236.064 56.3665Q242.943 63.6371 248.666 72.0005Q254.333 80.2811 258.59 89.2324L258.59 89.2325L258.59 89.233Q263.223 98.9771 266.185 109.516Q266.802 111.709 266.552 113.799Q266.303 115.889 265.188 117.876Q264.073 119.863 262.419 121.164Q260.765 122.466 258.572 123.082Q256.379 123.698 254.289 123.449Q252.199 123.2 250.212 122.085Q248.225 120.97 246.924 119.316Q245.622 117.662 245.006 115.469Q242.549 106.728 238.704 98.6482L238.704 98.6477Q235.189 91.263 230.514 84.4306Q225.771 77.4988 220.069 71.4742Q214.256 65.3312 207.445 60.1315Q200.108 54.5297 192.037 50.3456Q185.224 46.8143 177.889 44.2927Q170.33 41.6943 162.555 40.2886L162.555 40.2886Q153.392 38.6318 143.929 38.6318Q141.651 38.6318 139.706 37.8264Q137.761 37.0209 136.151 35.41Q134.54 33.7991 133.734 31.8546Q132.929 29.91 132.929 27.6318Q132.929 25.3537 133.734 23.4091Q134.54 21.4646 136.151 19.8537Q137.761 18.2427 139.706 17.4373Q141.651 16.6318 143.929 16.6318ZM264.26 110.057C249.176 56.3874 200.257 18.6318 143.929 18.6318C138.958 18.6318 134.929 22.6613 134.929 27.6318C134.929 32.6024 138.958 36.6318 143.929 36.6318C192.125 36.6318 234.012 68.96 246.931 114.928C248.276 119.713 253.246 122.502 258.031 121.157C262.816 119.812 265.605 114.842 264.26 110.057Z",
		fill: "paint_linear_7"
	},
	{
		d: "M143.929 18.6318C172.745 18.6318 200.087 28.4696 222.103 46.2153C225.973 49.3347 226.581 55.0006 223.462 58.8705C220.342 62.7404 214.676 63.3488 210.806 60.2295C191.961 45.0388 168.596 36.6318 143.929 36.6318C129.363 36.6318 115.219 39.5548 102.115 45.1541C97.5446 47.1072 92.256 44.9852 90.3029 40.4144C88.3498 35.8437 90.4718 30.555 95.0426 28.6019C110.372 22.0518 126.92 18.6318 143.929 18.6318Z",
		fill: "paint_linear_8"
	},
	{
		d: "M143.929 16.6318Q156.259 16.6318 168.141 18.9398L168.142 18.9399Q177.322 20.7231 186.235 23.884Q195.171 27.0533 203.444 31.4664Q213.934 37.0624 223.358 44.6582Q225.132 46.0879 226.14 47.9354Q227.148 49.7828 227.392 52.0479Q227.635 54.313 227.042 56.3325Q226.448 58.3519 225.019 60.1256Q223.589 61.8993 221.742 62.9078Q219.894 63.9163 217.629 64.1595Q215.364 64.4027 213.344 63.8095Q211.325 63.2163 209.551 61.7866Q201.586 55.3661 192.707 50.6766L192.706 50.6764Q186.051 47.1616 178.882 44.6191Q171.732 42.0834 164.369 40.6216Q154.346 38.6318 143.929 38.6318Q132.074 38.6318 120.796 41.1836L120.796 41.1837Q111.659 43.251 102.901 46.9933Q100.806 47.8884 98.7017 47.9118Q96.597 47.9352 94.4827 47.0869Q92.3684 46.2385 90.8637 44.7669Q89.3589 43.2952 88.4637 41.2003Q87.5686 39.1054 87.5452 37.0007Q87.5218 34.8961 88.3701 32.7818Q89.2185 30.6675 90.6901 29.1627Q92.1618 27.658 94.2567 26.7628Q105.084 22.1362 116.382 19.6225Q129.823 16.6318 143.929 16.6318ZM222.103 46.2153C200.087 28.4696 172.745 18.6318 143.929 18.6318C126.92 18.6318 110.372 22.0518 95.0426 28.6019C90.4718 30.555 88.3498 35.8437 90.3029 40.4144C92.256 44.9852 97.5446 47.1072 102.115 45.1541C115.219 39.5548 129.363 36.6318 143.929 36.6318C168.596 36.6318 191.961 45.0388 210.806 60.2295C214.676 63.3488 220.342 62.7404 223.462 58.8705C226.581 55.0006 225.973 49.3347 222.103 46.2153Z",
		fill: "paint_linear_9"
	},
	{
		d: "M111.532 22.893C116.332 21.6022 121.27 24.4471 122.56 29.2471C123.851 34.0471 121.006 38.9847 116.206 40.2755C86.3802 48.296 61.383 69.0766 47.802 96.888C40.6645 111.504 36.9028 127.61 36.9028 144.274C36.9028 149.244 32.8734 153.274 27.9028 153.274C22.9323 153.274 18.9028 149.244 18.9028 144.274C18.9028 124.858 23.295 106.053 31.6275 88.9896C47.48 56.5265 76.657 32.2713 111.532 22.893Z",
		fill: "paint_linear_10"
	},
	{
		d: "M111.013 20.9616Q113.213 20.37 115.3 20.6429Q117.387 20.9158 119.361 22.0531Q121.335 23.1904 122.617 24.8591Q123.9 26.5278 124.492 28.7277Q125.083 30.9277 124.81 33.0148Q124.538 35.1018 123.4 37.0757Q122.263 39.0497 120.594 40.3325Q118.926 41.6153 116.726 42.2069Q106.745 44.8907 97.6562 49.3795L97.6559 49.3796Q86.7845 54.7487 77.1883 62.7002Q68.3297 70.0405 61.393 78.8878Q54.565 87.5966 49.5992 97.7656Q44.7406 107.715 42.0889 118.222L42.0889 118.222Q38.9028 130.846 38.9028 144.274Q38.9028 146.552 38.0974 148.497Q37.2919 150.441 35.681 152.052Q34.0701 153.663 32.1256 154.468Q30.181 155.274 27.9028 155.274Q25.6246 155.274 23.6801 154.468Q21.7355 153.663 20.1247 152.052Q18.5138 150.441 17.7083 148.497Q16.9028 146.552 16.9028 144.274Q16.9028 128.304 20.6433 113.265Q23.8566 100.345 29.8303 88.112Q35.8369 75.8115 44.0988 65.2803Q52.4755 54.6029 63.1705 45.7442Q74.6026 36.275 87.5416 29.8322L87.5418 29.8322Q98.7153 24.2685 111.013 20.9616ZM122.56 29.2471C121.27 24.4471 116.332 21.6022 111.532 22.893C76.657 32.2713 47.48 56.5265 31.6275 88.9896C23.295 106.053 18.9028 124.858 18.9028 144.274C18.9028 149.244 22.9323 153.274 27.9028 153.274C32.8734 153.274 36.9028 149.244 36.9028 144.274C36.9028 127.61 40.6645 111.504 47.802 96.888C61.383 69.0766 86.3802 48.296 116.206 40.2755C121.006 38.9847 123.851 34.0471 122.56 29.2471Z",
		fill: "paint_linear_11"
	},
	{
		d: "M25.8173 102.973C27.4434 98.276 32.5694 95.7866 37.2664 97.4128C41.9635 99.039 44.4529 104.165 42.8267 108.862C38.9212 120.142 36.9028 132.063 36.9028 144.274C36.9028 175.241 49.9628 204.067 72.4189 224.363C76.1064 227.696 76.3939 233.387 73.061 237.075C69.7281 240.763 64.0368 241.05 60.3493 237.717C34.1529 214.04 18.9028 180.38 18.9028 144.274C18.9028 130.052 21.2581 116.141 25.8173 102.973Z",
		fill: "paint_linear_12"
	},
	{
		d: "M23.9273 102.319Q24.6727 100.166 26.07 98.5919Q27.4673 97.0179 29.5166 96.0226Q31.5659 95.0274 33.6669 94.9025L33.6669 94.9025Q35.768 94.7775 37.9208 95.5229Q40.0736 96.2682 41.6476 97.6655Q43.2216 99.0628 44.2168 101.112Q45.2121 103.161 45.337 105.262Q45.4619 107.364 44.7166 109.516Q42.386 116.248 40.9896 123.168Q38.9028 133.51 38.9028 144.274Q38.9028 156.705 41.6546 168.494L41.6546 168.494Q43.9244 178.218 48.0664 187.505Q52.3605 197.133 58.34 205.567L58.3401 205.567Q65.0036 214.965 73.7599 222.879Q75.4501 224.407 76.3526 226.309Q77.2551 228.21 77.3701 230.485Q77.485 232.76 76.7786 234.743Q76.0723 236.726 74.5447 238.416Q73.0171 240.106 71.1157 241.009Q69.2142 241.911 66.939 242.026Q64.6637 242.141 62.681 241.435Q60.6983 240.728 59.0082 239.201Q48.5336 229.734 40.5366 218.502L40.5365 218.502Q33.219 208.225 27.9759 196.471Q22.888 185.065 20.1379 173.12Q16.9028 159.07 16.9028 144.274Q16.9028 131.661 19.2834 119.515L19.2834 119.515Q20.9921 110.796 23.9273 102.319ZM37.2664 97.4128C32.5694 95.7866 27.4434 98.276 25.8173 102.973C21.2581 116.141 18.9028 130.052 18.9028 144.274C18.9028 180.38 34.1529 214.04 60.3493 237.717C64.0368 241.05 69.7281 240.763 73.061 237.075C76.3939 233.387 76.1064 227.696 72.4189 224.363C49.9628 204.067 36.9028 175.241 36.9028 144.274C36.9028 132.063 38.9212 120.142 42.8267 108.862C44.4529 104.165 41.9635 99.039 37.2664 97.4128Z",
		fill: "paint_linear_13"
	}
];
function Jp(e) {
	return /* @__PURE__ */ h("g", {
		transform: `scale(${e})`,
		children: [/* @__PURE__ */ m("path", {
			d: "M14.3423 2.72888L3.19415 17.5587C1.8791 19.308 3.1272 21.8077 5.31571 21.8077L28.3843 21.8077C30.6127 21.8077 31.8491 19.2275 30.453 17.4907L18.5325 2.66088C17.4479 1.31151 15.3826 1.34502 14.3423 2.72888Z",
			fill: "rgb(0,0,0)",
			fillOpacity: .898039222,
			fillRule: "evenodd",
			transform: "matrix(0.743145,0.669131,-0.669131,0.743145,207.983,47.0181)"
		}), /* @__PURE__ */ m("path", {
			d: "M11.3115 0.450507Q12.2589 -0.809787 13.5208 -1.45273Q14.7828 -2.09567 16.3592 -2.12125Q17.9357 -2.14683 19.2179 -1.54518Q20.5 -0.943523 21.4878 0.28537L33.4083 15.1152Q34.0695 15.9378 34.425 16.8764Q34.7251 17.6688 34.8072 18.5439Q34.8858 19.3815 34.7543 20.1848L34.7542 20.1849Q34.6071 21.0835 34.1972 21.939Q33.7872 22.7946 33.179 23.4722Q32.6353 24.078 31.9331 24.5416Q31.1997 25.0259 30.394 25.2884Q29.4398 25.5994 28.3843 25.5994L5.31571 25.5994Q3.3226 25.5994 1.88087 24.7078Q0.439138 23.8162 -0.451216 22.033Q-1.34157 20.2498 -1.18793 18.5616Q-1.03429 16.8735 0.163347 15.2803L11.3115 0.450507ZM3.19415 17.5587L14.3423 2.72888C15.3826 1.34502 17.4479 1.31151 18.5325 2.66088L30.453 17.4907C31.8491 19.2275 30.6127 21.8077 28.3843 21.8077L5.31571 21.8077C3.1272 21.8077 1.8791 19.308 3.19415 17.5587Z",
			fill: "rgb(255,255,255)",
			fillRule: "evenodd",
			transform: "matrix(0.743145,0.669131,-0.669131,0.743145,207.983,47.0181)"
		})]
	});
}
function Yp(e, t) {
	let n = e === "Large" ? 1 : e === "Small" ? 136 / 288 : 88 / 288;
	return /* @__PURE__ */ h(p, { children: [
		/* @__PURE__ */ m("defs", { children: Kp.map((e) => /* @__PURE__ */ m("linearGradient", {
			id: `${t}-${e.id}`,
			x1: e.x1,
			y1: e.y1,
			x2: e.x2,
			y2: e.y2,
			gradientUnits: "userSpaceOnUse",
			children: e.stops.map((t) => /* @__PURE__ */ m("stop", {
				offset: t.offset,
				stopColor: t.color,
				stopOpacity: t.stopOpacity
			}, `${e.id}-${t.offset}`))
		}, e.id)) }),
		/* @__PURE__ */ m("g", {
			transform: `scale(${n})`,
			children: qp.map((e, n) => /* @__PURE__ */ m("path", {
				d: e.d,
				fill: e.fill ? `url(#${t}-${e.fill})` : "none",
				fillRule: "evenodd",
				stroke: e.stroke ? `url(#${t}-${e.stroke})` : void 0,
				strokeWidth: e.strokeWidth
			}, `exact-multi-${n}`))
		}),
		Jp(n)
	] });
}
function Xp(e, t, n, r, i, a, o) {
	let s = 1.6, c = Math.max(1.25, t * .22), l = 0, u = n.map((e, t) => {
		let n = Math.max(e.percentage - s, 0), c = l + s / 2, u = c + n, d = a + c / 100 * (o - a), f = a + u / 100 * (o - a), p = Bp(r, r, i, d), m = Bp(r, r, i, f), h = Vp(r, r, i, d, f), g = `gauge-multi-outline-${t}-${e.color.replace("#", "")}`;
		return l += e.percentage, {
			color: e.color,
			colorPath: h,
			outlineGradientId: g,
			gradientStart: p,
			gradientEnd: m,
			originalIndex: t
		};
	}), d = u.map((e, n) => /* @__PURE__ */ h("g", { children: [/* @__PURE__ */ m("defs", { children: /* @__PURE__ */ h("linearGradient", {
		id: e.outlineGradientId,
		gradientUnits: "userSpaceOnUse",
		x1: e.gradientStart.x,
		y1: e.gradientStart.y,
		x2: e.gradientEnd.x,
		y2: e.gradientEnd.y,
		children: [/* @__PURE__ */ m("stop", {
			offset: "0%",
			stopColor: "#FFFFFF",
			stopOpacity: "1"
		}), /* @__PURE__ */ m("stop", {
			offset: "100%",
			stopColor: "#FFFFFF",
			stopOpacity: "0"
		})]
	}) }), /* @__PURE__ */ m(Gp, {
		path: e.colorPath,
		stroke: `url(#${e.outlineGradientId})`,
		strokeWidth: t + c * 2,
		opacity: .95
	})] }, `outline-${e.color}-${n}`)), f = [...u].reverse().map((e, r) => {
		let i = n[e.originalIndex], a = !!(i.gradientStops && i.gradientStops.length > 0), o = a ? `gauge-multi-color-${e.originalIndex}-${i.color.replace("#", "")}` : null;
		return /* @__PURE__ */ h("g", { children: [a && o ? /* @__PURE__ */ m("defs", { children: /* @__PURE__ */ m("linearGradient", {
			id: o,
			gradientUnits: "userSpaceOnUse",
			x1: e.gradientEnd.x,
			y1: e.gradientEnd.y,
			x2: e.gradientStart.x,
			y2: e.gradientStart.y,
			children: i.gradientStops.map((e) => /* @__PURE__ */ m("stop", {
				offset: e.offset,
				stopColor: e.color,
				stopOpacity: e.stopOpacity ?? 1
			}, e.offset))
		}) }) : null, /* @__PURE__ */ m(Gp, {
			path: e.colorPath,
			stroke: a && o ? `url(#${o})` : e.color,
			strokeWidth: t
		})] }, `color-${e.color}-${r}`);
	});
	return [...d, ...f];
}
function Zp(e, t, n, r) {
	return e === "Progress" ? null : (e === "Line" || e === "Double Data") && n && r ? /* @__PURE__ */ h("div", {
		className: "hm-gauge-ring__bottom-row",
		children: [/* @__PURE__ */ m("span", { children: n }), /* @__PURE__ */ m("span", { children: r })]
	}) : t ? /* @__PURE__ */ m("div", {
		className: "hm-gauge-ring__bottom-label",
		children: t
	}) : null;
}
function Qp({ 类型: e = "Default", 尺寸: t = "Large", 数值: n, 标签: r, 说明: i, 左值: a, 右值: o, 进度: s, 分段: l, className: u, style: d, ...f }) {
	let g = c().replace(/:/g, ""), _ = Ap[t], v = zp[e][t], y = String(n ?? v.数值), b = i ?? v.说明, x = r ?? v.标签, S = a === void 0 ? v.左值 : String(a), C = o === void 0 ? v.右值 : String(o), w = Hp(s, v.进度 ?? 84), T = l ?? (t === "Small" || t === "Mini" ? Ip : Fp), E = e === "Default", D = e === "Progress", O = e === "Line", k = e === "Double Data", A = e === "Multi Segment", j = O ? Rp[t] : Lp, M = `gauge-gradient-${g}-${e.replace(/\s+/g, "-")}-${t}`, N = `gauge-multi-exact-${g}-${t}`, P = _.container / 2, F = O || k ? t === "Large" ? Np : t === "Small" ? Pp : 0 : 0, I = jp + F, L = Mp - F, R = Vp(P, P, _.radius, I, L), z = A, B = E || O || A && !!l, V = E ? _.defaultMainSize : _.standardMainSize, H = E ? _.defaultMainLine : _.standardMainLine, ee = {
		width: _.container,
		height: _.container,
		"--hm-gauge-main-top": `${_.mainTop}px`,
		"--hm-gauge-main-size": `${V}px`,
		"--hm-gauge-main-line": `${H}px`,
		"--hm-gauge-subtitle-size": `${_.subtitleSize}px`,
		"--hm-gauge-subtitle-line": `${_.subtitleLine}px`,
		"--hm-gauge-subtitle-gap": `${_.subtitleGap}px`,
		"--hm-gauge-bottom-label-size": `${_.bottomLabelSize}px`,
		"--hm-gauge-bottom-label-line": `${_.bottomLabelLine}px`,
		"--hm-gauge-bottom-label-bottom": `${_.bottomLabelBottom}px`,
		"--hm-gauge-bottom-row-size": `${_.bottomRowSize}px`,
		"--hm-gauge-bottom-row-line": `${_.bottomRowLine}px`,
		"--hm-gauge-bottom-row-bottom": `${_.bottomRowBottom}px`,
		"--hm-gauge-arrow-top": `${_.arrowTop}px`,
		"--hm-gauge-arrow-left": `${_.arrowLeft}px`,
		"--hm-gauge-arrow-right": `${_.arrowRight}px`,
		"--hm-gauge-arrow-size": `${_.arrowSize}px`,
		"--hm-gauge-runner-bottom": `${_.runnerBottom}px`,
		...d
	};
	return /* @__PURE__ */ h("div", {
		className: X("hm-gauge-ring", `hm-gauge-ring--${t}`, `hm-gauge-ring--${e.replace(/\s+/g, "-")}`, u),
		style: ee,
		...f,
		children: [
			/* @__PURE__ */ h("svg", {
				className: "hm-gauge-ring__svg",
				viewBox: `0 0 ${_.container} ${_.container}`,
				width: _.container,
				height: _.container,
				fill: "none",
				xmlns: "http://www.w3.org/2000/svg",
				children: [
					/* @__PURE__ */ h("defs", { children: [/* @__PURE__ */ m("linearGradient", {
						id: M,
						x1: "0%",
						y1: "82%",
						x2: "100%",
						y2: "10%",
						children: j.map((e) => /* @__PURE__ */ m("stop", {
							offset: e.offset,
							stopColor: e.color
						}, `${M}-${e.offset}`))
					}), /* @__PURE__ */ m("filter", {
						id: `gauge-glow-${t}`,
						x: "-30%",
						y: "-30%",
						width: "160%",
						height: "160%",
						children: /* @__PURE__ */ m("feGaussianBlur", { stdDeviation: t === "Large" ? 6 : 3 })
					})] }),
					E && t === "Large" ? /* @__PURE__ */ m(Gp, {
						path: R,
						stroke: `url(#${M})`,
						strokeWidth: _.stroke + 4,
						opacity: .35,
						filter: `url(#gauge-glow-${t})`
					}) : null,
					E || O ? /* @__PURE__ */ m(Gp, {
						path: R,
						stroke: `url(#${M})`,
						strokeWidth: _.stroke
					}) : null,
					k ? /* @__PURE__ */ h(p, { children: [/* @__PURE__ */ m(Gp, {
						path: R,
						stroke: "rgba(250, 185, 181, 0.95)",
						strokeWidth: _.stroke
					}), /* @__PURE__ */ m(Gp, {
						path: R,
						stroke: "#F7453E",
						strokeWidth: _.stroke,
						dasharray: `${w} ${100 - w}`,
						dashoffset: -(100 - w)
					})] }) : null,
					D ? /* @__PURE__ */ h(p, { children: [/* @__PURE__ */ m(Gp, {
						path: R,
						stroke: "rgba(220, 242, 175, 0.95)",
						strokeWidth: _.stroke
					}), /* @__PURE__ */ m(Gp, {
						path: R,
						stroke: "#B6E60F",
						strokeWidth: _.stroke,
						dasharray: `${w} ${100 - w}`,
						dashoffset: -(100 - w)
					})] }) : null,
					A ? l ? Xp(R, _.stroke, T, P, _.radius, I, L) : Yp(t, N) : null
				]
			}),
			B ? /* @__PURE__ */ m("div", {
				className: X("hm-gauge-ring__arrow", z ? "hm-gauge-ring__arrow--right" : "hm-gauge-ring__arrow--left"),
				children: /* @__PURE__ */ m(Up, { size: _.arrowSize })
			}) : null,
			/* @__PURE__ */ h("div", {
				className: "hm-gauge-ring__center",
				children: [/* @__PURE__ */ m("div", {
					className: "hm-gauge-ring__value",
					children: y
				}), b ? /* @__PURE__ */ m("div", {
					className: "hm-gauge-ring__subtitle",
					children: b
				}) : null]
			}),
			D ? /* @__PURE__ */ m("div", {
				className: "hm-gauge-ring__runner",
				children: /* @__PURE__ */ m(Wp, { size: _.runnerSize })
			}) : Zp(e, x, S, C)
		]
	});
}
//#endregion
//#region src/components/Views/GaugeRing/index.ts
var $p = /* @__PURE__ */ _({
	GaugeRing: () => Qp,
	default: () => Qp
}), em = [
	"Pure Color",
	"Multi Color",
	"Progress",
	"Double Progress",
	"Percentage"
], tm = [
	"Small",
	"Medium",
	"Large"
], nm = {
	Small: {
		width: 128,
		height: 20,
		trackThickness: 6,
		trackLength: 80,
		fontSize: 12,
		markerFontSize: 12,
		bottomFontSize: 10,
		gap: 8,
		radius: 6,
		arrowWidth: 10,
		arrowHeight: 6,
		arrowStrokeWidth: 1.5,
		arrowOverlap: 2
	},
	Medium: {
		width: 170,
		height: 24,
		trackThickness: 8,
		trackLength: 118,
		fontSize: 14,
		markerFontSize: 14,
		bottomFontSize: 10,
		gap: 8,
		radius: 6,
		arrowWidth: 12,
		arrowHeight: 8,
		arrowStrokeWidth: 2.5,
		arrowOverlap: 3
	},
	Large: {
		width: 214,
		height: 26,
		trackThickness: 10,
		trackLength: 158,
		fontSize: 16,
		markerFontSize: 14,
		bottomFontSize: 14,
		gap: 8,
		radius: 6,
		arrowWidth: 16,
		arrowHeight: 10,
		arrowStrokeWidth: 3.5,
		arrowOverlap: 4
	}
}, rm = {
	Small: {
		width: 36,
		height: 226,
		trackThickness: 6,
		trackLength: 178
	},
	Medium: {
		width: 36,
		height: 226,
		trackThickness: 8,
		trackLength: 178
	},
	Large: {
		width: 36,
		height: 226,
		trackThickness: 10,
		trackLength: 168
	}
}, im = {
	Small: 24,
	Medium: 30,
	Large: 37
}, am = "rgba(232, 64, 38, 1)", om = "rgba(70, 177, 227, 0.3)", sm = "rgba(70, 177, 227, 1)", cm = [
	{
		widthRatio: 3.14 / 214,
		colorClass: "hm-strip-gauge__segment--1"
	},
	{
		widthRatio: 4.71 / 214,
		colorClass: "hm-strip-gauge__segment--2"
	},
	{
		widthRatio: 6.28 / 214,
		colorClass: "hm-strip-gauge__segment--3"
	},
	{
		widthRatio: 7.85 / 214,
		colorClass: "hm-strip-gauge__segment--4"
	},
	{
		widthRatio: 9.42 / 214,
		colorClass: "hm-strip-gauge__segment--5"
	},
	{
		widthRatio: 18.84 / 214,
		colorClass: "hm-strip-gauge__segment--6"
	},
	{
		widthRatio: 53.38 / 214,
		colorClass: "hm-strip-gauge__segment--7"
	}
], lm = {
	"Pure Color": {
		Small: {
			起始值: "18",
			结束值: "30",
			当前值: "26",
			进度: 100
		},
		Medium: {
			起始值: "18",
			结束值: "30",
			当前值: "26",
			进度: 100
		},
		Large: {
			起始值: "18",
			结束值: "30",
			当前值: "26",
			进度: 100
		}
	},
	"Multi Color": {
		Small: {
			起始值: "18",
			结束值: "30",
			当前值: "26",
			进度: 100
		},
		Medium: {
			起始值: "18",
			结束值: "30",
			当前值: "26",
			进度: 100
		},
		Large: {
			起始值: "18",
			结束值: "30",
			当前值: "26",
			进度: 100
		}
	},
	Progress: {
		Small: {
			起始值: "18",
			结束值: "30",
			进度: 78
		},
		Medium: {
			起始值: "18",
			结束值: "30",
			进度: 78
		},
		Large: {
			起始值: "18",
			结束值: "30",
			进度: 82
		}
	},
	"Double Progress": {
		Small: {
			起始值: "18",
			结束值: "30",
			进度: 68
		},
		Medium: {
			起始值: "18",
			结束值: "30",
			进度: 68
		},
		Large: {
			起始值: "18",
			结束值: "30",
			进度: 68
		}
	},
	Percentage: {
		Small: {
			起始值: "",
			结束值: "",
			进度: 100,
			标签: "Phone",
			值文本: "123GB/500GB"
		},
		Medium: {
			起始值: "",
			结束值: "",
			进度: 100,
			标签: "Phone",
			值文本: "123GB/500GB"
		},
		Large: {
			起始值: "",
			结束值: "",
			进度: 100,
			标签: "Phone222",
			值文本: "123GB/500GB"
		}
	}
};
function um(e, t, n) {
	return Math.max(t, Math.min(n, e));
}
function dm({ vertical: e, markerPercent: t, value: n, fontSize: r, arrowWidth: i, arrowHeight: a, arrowStrokeWidth: o, arrowOverlap: s }) {
	let c = um(t, 0, 100), l = e ? { bottom: `${c}%` } : { left: `${c}%` }, u = "var(--harmony-font-primary, rgba(0,0,0,0.898))", d = "var(--harmony-background-primary, rgba(255,255,255,1))", f = i / 2, g = `${f},0 0,${a} ${i},${a}`, _ = `${a},${f} 0,0 0,${i}`, v = e ? _ : g, y = e ? a : i, b = e ? i : a, x = o, S = y + x * 2, C = b + x * 2, w = e ? {
		flexShrink: 0,
		display: "block",
		marginRight: -s
	} : {
		flexShrink: 0,
		display: "block",
		marginTop: -s
	};
	return /* @__PURE__ */ m("div", {
		className: "hm-strip-gauge__marker",
		style: l,
		children: e ? /* @__PURE__ */ h(p, { children: [/* @__PURE__ */ m("span", {
			className: "hm-strip-gauge__marker-value",
			style: { fontSize: `${r}px` },
			children: n
		}), /* @__PURE__ */ h("svg", {
			width: S,
			height: C,
			viewBox: `${-x} ${-x} ${S} ${C}`,
			style: w,
			children: [/* @__PURE__ */ m("polygon", {
				points: v,
				fill: "none",
				stroke: d,
				strokeWidth: o * 2,
				strokeLinejoin: "round"
			}), /* @__PURE__ */ m("polygon", {
				points: v,
				fill: u,
				stroke: "none"
			})]
		})] }) : /* @__PURE__ */ h(p, { children: [/* @__PURE__ */ h("svg", {
			width: S,
			height: C,
			viewBox: `${-x} ${-x} ${S} ${C}`,
			style: w,
			children: [/* @__PURE__ */ m("polygon", {
				points: v,
				fill: "none",
				stroke: d,
				strokeWidth: o * 2,
				strokeLinejoin: "round"
			}), /* @__PURE__ */ m("polygon", {
				points: v,
				fill: u,
				stroke: "none"
			})]
		}), /* @__PURE__ */ m("span", {
			className: "hm-strip-gauge__marker-value",
			style: { fontSize: `${r}px` },
			children: n
		})] })
	});
}
function fm({ vertical: e, trackLength: t, trackThickness: n }) {
	let r = t / 214, i = [
		53.38,
		18.84,
		9.42,
		7.85,
		6.28,
		4.71,
		3.14
	];
	return /* @__PURE__ */ m("div", {
		className: "hm-strip-gauge__segments",
		children: cm.map((t, a) => {
			let o = i[a] * r, s = e ? {
				height: `${o}px`,
				width: `${n}px`
			} : {
				width: `${o}px`,
				height: `${n}px`
			};
			return /* @__PURE__ */ m("div", {
				className: X("hm-strip-gauge__segment", t.colorClass),
				style: s
			}, a);
		})
	});
}
function pm({ 类型: e = "Pure Color", 尺寸: t = "Large", vertical: n = !1, 起始值: r, 结束值: i, 当前值: a, 进度: o, 第二进度: s, 标签: c, 值文本: l, className: u, style: d, ...f }) {
	let p = nm[t], g = rm[t], _ = lm[e][t], v = n, y = e === "Percentage", b = e === "Pure Color", x = e === "Multi Color", S = e === "Progress", C = e === "Double Progress", w = b || x, T = !y, E = r ?? _.起始值, D = i ?? _.结束值, O = a ?? _.当前值 ?? "", k = um(o ?? _.进度, 0, 100), A = e === "Pure Color" ? am : e === "Multi Color" ? "transparent" : e === "Progress" ? om : "var(--harmony-comp-background-secondary)", j, M;
	v ? (j = g.width, M = g.height) : y ? (j = p.width, M = im[t]) : (j = p.width, M = p.height);
	let N = v ? g.trackThickness : p.trackThickness, P = y ? j : v ? g.trackLength : p.trackLength, F = p.fontSize, I = p.gap, L = parseFloat(E) || 0, R = parseFloat(D) || 1, z = R === L ? 50 : um(((parseFloat(O) || L) - L) / (R - L) * 100, 0, 100), B = w ? p.markerFontSize + 4 : 0, V = {
		width: v ? void 0 : `${j}px`,
		minHeight: `${M}px`,
		...B && !v ? { paddingBottom: `${B}px` } : {},
		...B && v ? { paddingLeft: `${B}px` } : {},
		"--hm-strip-gauge-gap": `${I}px`,
		"--hm-strip-gauge-track-width": v ? `${N}px` : void 0,
		"--hm-strip-gauge-track-radius": `${p.radius}px`,
		"--hm-strip-gauge-track-bg": A,
		"--hm-strip-gauge-bottom-font-size": `${p.bottomFontSize}px`,
		...d
	}, H = v ? {
		width: `${N}px`,
		height: `${P}px`
	} : {
		width: `${P}px`,
		height: `${N}px`
	};
	return /* @__PURE__ */ h("div", {
		className: X("hm-strip-gauge", v ? "hm-strip-gauge--vertical" : "hm-strip-gauge--horizontal", y && "hm-strip-gauge--percentage", u),
		style: V,
		...f,
		children: [
			y && /* @__PURE__ */ h("div", {
				className: "hm-strip-gauge__bottom-row",
				children: [/* @__PURE__ */ m("span", {
					className: "hm-strip-gauge__bottom-label",
					children: c ?? _.标签
				}), /* @__PURE__ */ m("span", {
					className: "hm-strip-gauge__bottom-value",
					children: l ?? _.值文本
				})]
			}),
			T && /* @__PURE__ */ m("span", {
				className: "hm-strip-gauge__value",
				style: { fontSize: `${F}px` },
				children: E
			}),
			/* @__PURE__ */ m("div", {
				className: "hm-strip-gauge__track-wrapper",
				children: /* @__PURE__ */ h("div", {
					className: X("hm-strip-gauge__track", x && "hm-strip-gauge__track--multi-color"),
					style: H,
					children: [/* @__PURE__ */ h("div", {
						className: "hm-strip-gauge__track-inner",
						children: [
							b && /* @__PURE__ */ m("div", {
								className: "hm-strip-gauge__fill hm-strip-gauge__fill--pure-color",
								style: { backgroundColor: am }
							}),
							S && /* @__PURE__ */ m("div", {
								className: "hm-strip-gauge__fill hm-strip-gauge__fill--progress",
								style: {
									backgroundColor: sm,
									...v ? {
										height: `${k}%`,
										width: "100%"
									} : {
										width: `${k}%`,
										height: "100%"
									}
								}
							}),
							C && /* @__PURE__ */ m("div", {
								className: "hm-strip-gauge__fill hm-strip-gauge__fill--double-progress hm-strip-gauge__fill--gradient-green-yellow",
								style: { ...v ? {
									height: `${k}%`,
									width: "100%"
								} : {
									width: `${k}%`,
									height: "100%"
								} }
							}),
							y && /* @__PURE__ */ m(fm, {
								vertical: v,
								trackLength: P,
								trackThickness: N
							})
						]
					}), w && /* @__PURE__ */ m(dm, {
						vertical: v,
						markerPercent: z,
						value: O,
						fontSize: p.markerFontSize,
						arrowWidth: p.arrowWidth,
						arrowHeight: p.arrowHeight,
						arrowStrokeWidth: p.arrowStrokeWidth,
						arrowOverlap: p.arrowOverlap
					})]
				})
			}),
			T && /* @__PURE__ */ m("span", {
				className: "hm-strip-gauge__value",
				style: { fontSize: `${F}px` },
				children: D
			})
		]
	});
}
//#endregion
//#region src/components/Views/GaugeStripGauge/index.ts
var mm = /* @__PURE__ */ _({
	GaugeStripGauge: () => pm,
	default: () => pm,
	gaugeStripGaugeSizes: () => tm,
	gaugeStripGaugeTypes: () => em
});
//#endregion
//#region src/components/Views/ProgressBar/progress-bar.tsx
function hm({ 进度: e = 43, Cache: t = !1, Cache进度: n = 58, className: r, ...i }) {
	return /* @__PURE__ */ m("div", {
		className: X("hm-progress-bar", r),
		style: {
			"--progress-bar-progress": `${e}%`,
			"--progress-bar-cache": `${t ? n : 0}%`
		},
		...i,
		children: /* @__PURE__ */ h("div", {
			className: "hm-progress-bar__track",
			children: [t && /* @__PURE__ */ m("div", { className: "hm-progress-bar__cache" }), /* @__PURE__ */ m("div", { className: "hm-progress-bar__fill" })]
		})
	});
}
//#endregion
//#region src/components/Views/ProgressBar/progress-bar.constants.ts
var gm = [!1, !0], _m = /* @__PURE__ */ _({
	ProgressBar: () => hm,
	progressBarCacheOptions: () => gm
}), vm = [
	"Enabled",
	"Hover",
	"Pressed",
	"Focus",
	"Disabled"
];
function ym({ 状态: e = "Enabled", value: t = 27, className: n, style: r, ...i }) {
	let a = Math.max(0, Math.min(100, t));
	return /* @__PURE__ */ h("div", {
		className: X("hm-progress-bar-capsule", n),
		"data-状态": e,
		style: {
			...r,
			"--hm-progress-capsule-fill-width": `${a}%`
		},
		...i,
		children: [/* @__PURE__ */ m("div", {
			className: "hm-progress-bar-capsule__track",
			children: /* @__PURE__ */ m("div", {
				className: "hm-progress-bar-capsule__fill",
				style: { width: `${a}%` }
			})
		}), /* @__PURE__ */ h("span", {
			className: "hm-progress-bar-capsule__text",
			children: [a, "%"]
		})]
	});
}
//#endregion
//#region src/components/Views/ProgressBarCapsule/index.ts
var bm = /* @__PURE__ */ _({
	ProgressBarCapsule: () => ym,
	progressBarCapsuleStates: () => vm
}), xm = "data:image/png;base64,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", Sm = ["OFF", "ON"];
function Cm({ withIcon: e = "OFF", 进度: t = 74, 图标: n, className: r, ...i }) {
	let a = Math.max(0, Math.min(100, t)), o = e === "ON", s = a / 100 * 16;
	return /* @__PURE__ */ m("div", {
		className: X("pbe", o && "pbe--on", r),
		role: "progressbar",
		"aria-valuenow": a,
		"aria-valuemin": 0,
		"aria-valuemax": 100,
		"aria-label": `进度 ${a}%`,
		...i,
		children: o ? /* @__PURE__ */ h(p, { children: [
			/* @__PURE__ */ m("img", {
				className: "pbe__appicon",
				src: xm,
				alt: ""
			}),
			n && /* @__PURE__ */ m("span", {
				className: "pbe__appicon--custom",
				children: n
			}),
			/* @__PURE__ */ m("div", {
				className: "pbe__boolean",
				style: {
					WebkitMaskImage: `radial-gradient(circle ${s}px at 24px 24px, transparent ${s}px, black ${s}px)`,
					maskImage: `radial-gradient(circle ${s}px at 24px 24px, transparent ${s}px, black ${s}px)`
				}
			})
		] }) : /* @__PURE__ */ h(p, { children: [
			/* @__PURE__ */ m("div", { className: "pbe__sun" }),
			/* @__PURE__ */ m("div", {
				className: "pbe__moon-clip",
				children: /* @__PURE__ */ m("div", {
					className: "pbe__moon",
					style: { left: `${-48 + a / 100 * 48}px` }
				})
			}),
			/* @__PURE__ */ h("span", {
				className: "pbe__pct",
				children: [a, "%"]
			})
		] })
	});
}
//#endregion
//#region src/components/Views/ProgressBarEclipse/index.ts
var wm = /* @__PURE__ */ _({
	ProgressBarEclipse: () => Cm,
	progressBarEclipseIcons: () => Sm
}), Tm = [
	"24",
	"32",
	"40",
	"72"
], Em = {
	24: { strokeWidth: 2 },
	32: { strokeWidth: 1.875 },
	40: { strokeWidth: 1.8 },
	72: { strokeWidth: 1.333 }
};
function Dm({ 尺寸: e = "40", className: t, ...n }) {
	let r = Em[e];
	return /* @__PURE__ */ m("div", {
		className: X("hm-progress-bar-loading", `hm-progress-bar-loading--${e}`, t),
		role: "progressbar",
		"aria-label": "加载中",
		...n,
		children: /* @__PURE__ */ m(Om, {
			size: Number(e),
			strokeWidth: r.strokeWidth,
			className: "hm-progress-bar-loading__spinner"
		})
	});
}
function Om({ size: e, strokeWidth: t, className: n, ...r }) {
	let i = `hm-progress-bar-loading-gradient-${c().replace(/:/g, "")}`, a = 8.75, o = 2 * Math.PI * a;
	return /* @__PURE__ */ h("svg", {
		width: e,
		height: e,
		viewBox: "0 0 24 24",
		fill: "none",
		className: n,
		"aria-hidden": "true",
		...r,
		children: [
			/* @__PURE__ */ m("defs", { children: /* @__PURE__ */ h("linearGradient", {
				id: i,
				x1: "19",
				y1: "5",
				x2: "5",
				y2: "19",
				gradientUnits: "userSpaceOnUse",
				children: [
					/* @__PURE__ */ m("stop", {
						offset: "0%",
						stopColor: "currentColor",
						stopOpacity: "1"
					}),
					/* @__PURE__ */ m("stop", {
						offset: "55%",
						stopColor: "currentColor",
						stopOpacity: "0.65"
					}),
					/* @__PURE__ */ m("stop", {
						offset: "100%",
						stopColor: "currentColor",
						stopOpacity: "0"
					})
				]
			}) }),
			/* @__PURE__ */ m("circle", {
				cx: "12",
				cy: "12",
				r: a,
				stroke: "currentColor",
				strokeWidth: t,
				className: "hm-progress-bar-loading__track"
			}),
			/* @__PURE__ */ m("g", {
				className: "hm-progress-bar-loading__rotor",
				children: /* @__PURE__ */ m("circle", {
					cx: "12",
					cy: "12",
					r: a,
					stroke: `url(#${i})`,
					strokeWidth: t,
					strokeDasharray: `${o * .76} ${o}`,
					strokeLinecap: "round",
					className: "hm-progress-bar-loading__arc"
				})
			})
		]
	});
}
//#endregion
//#region src/components/Views/ProgressBarLoading/index.ts
var km = /* @__PURE__ */ _({
	ProgressBarLoading: () => Dm,
	progressBarLoadingSizes: () => Tm
}), Am = [
	"Routine",
	"Avatar",
	"Icon",
	"Default"
], jm = [
	"Default",
	"Error",
	"Loading"
], Mm = [
	"111111101110101111111",
	"100000101010101000001",
	"101110101001001011101",
	"101110101111101011101",
	"101110100000001011101",
	"100000101100001000001",
	"111111101010101111111",
	"000000000111100000000",
	"110011100100000101111",
	"001110011100110011110",
	"110110110100111101001",
	"110011001100001001110",
	"011001100011110101101",
	"000000001000000010010",
	"111111100110111001111",
	"100000101001111110111",
	"101110101000110010000",
	"101110100001101001111",
	"101110100111100100100",
	"100000101001101001100",
	"111111101000000011001"
].flatMap((e, t) => Array.from(e, (e, n) => e === "1" ? `M${n} ${t}h1v1h-1z` : "")).join("");
function Nm({ 类型: e = "Routine", 状态: t = "Default", avatarSrc: n, iconSrc: r, errorText: i = "The QR code has expired, click refresh", onRefresh: a, className: o }) {
	let s = t === "Error" || t === "Loading", c = e === "Avatar" && t === "Default", l = e === "Icon" && t === "Default", u = t === "Error", d = t === "Loading";
	return /* @__PURE__ */ h("div", {
		className: X("qrcode-container", o),
		"data-type": e,
		"data-state": t,
		children: [
			/* @__PURE__ */ m("div", {
				className: X("qrcode-area", s && "qrcode-area--dimmed"),
				children: /* @__PURE__ */ m(Pm, {})
			}),
			c && /* @__PURE__ */ m("div", {
				className: "qrcode-avatar-layer",
				children: /* @__PURE__ */ m("div", {
					className: "qrcode-avatar-placeholder",
					children: /* @__PURE__ */ m("img", {
						src: n || "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAHAAAABwCAYAAADG4PRLAABmo0lEQVR4Ae3gAZAkSZIkSRKLqpm7R0REZmZmVlVVVVV3d3d3d/fMzMzMzMzMzMzMzMzMzMzMzMzMzMzMzMzMzMzMzMzMzMzMzMzMzMzMzMzMzMzMzMzMzMzMzMzMzMzMzMzMzMzMzMzMzMzMzMzMzMzMzMzMzMzMzMzMdHd3d3dXV1VVVVVmZkZGRIS7m5kKz0xmV3d1d3dPz8zMzMxMovhf6Bc/4k1mbrPH0HiMaveIDenB8nhTFddszRenOrFN5oZMnSTGKad0Oxqy7S8b5w9d7jvIvOOO/cNbh9I/WXX++O3tg8d/5Nf90pr/XRD/C/zoJ7z3deNUXtvZXkvT+IrzyBef5dRfOlphxLVbc3K9ZL1ecfr4cTa7HjnBSQhMcJTmsDX2x+S8ZqyicuHogHEyiwiORw4z/Pdnj9Z/et/k39HW9m9/2Xf/2D38z4b4H+onPvCdXnYYD99mIt5s6BYvs+5mOBNaoyvQ58Rt95xlnEau3VhwalFRG7m4f8CLPeTBzEIokyRZqnL3EOwZmsS+C1N0LJf79K2xVTumNrB7eMgYldbNKbVjU/6rG/vyC9Xtp973W3/kL/mfB/E/yC982Ls+aI3fq5l39Tg8arU6YGzgKCxrx34zy2FgY2OT1eEhd9x7lhOLnsPlyMNObnBiFjz5rrPcfO0Zbj51Ak+NtcR+mXPehexn9LMZpNA0EusjIpOhNe7b2+PSes3msZPMNrY5Xs1sGqnZSJut+eKJx/ruB49tzL/n9b7gG57B/wyI/wF+/oPf7o2ilI9s6t/kCJTZKNOa1WrN0dQoglt397i4biw2FoTEpcMl+0crFm7cfmnJma05jzyzzbm9Q3bXEzdcc5ozp09Bt6Cfz1kU0ZdChMhpog0Dy/WKw/XAxaMly0xcZ2xsbLLR92yQtGHNkEmZzTmxmHE84HSxZ/iXZm31ta/0NT/6K/z3Qvw3MehH3vvN3imifmrpZy/RzXomi3UaZ6NrI6tx4Nxq5HF33sudu/tcd/I4G10QJbhvd8nu0ZKHnz7O7ZcOOXuw5LqdBTXE3rqxOV/wYg+7mRObm2wVcaoPWiZDS/bWA+eO1uwPa8Y0YzYiKlvzBddubrBTxWpq7C4HDlXodo4xm3Wc6QvXHV3gOI15JLT2d5ntC1/+63/2RyTMfz3Ef4PvfY83e9u+6guIeDR1BrUnukq2xtFqxWpodEpaNv7itrv5h7sv8rBrjnHNzgYHR2sOp+S2c5cgzYNPHWMgufXCASD6EqymxulFz6s99AYece1p0rCaJi6uByZgTTBEoe8KNYIcRiIbx2czTnaFziPn143bD0cO6pwyXzCb91x7bIfrj85zar1HH6ZkYsPY8gmXVutPe/Pv+/Wf5L8W4r/Q177rm7/iouqr58GrzEqg2pFdz6jACoZx5HC5YjVMFAXJxK/8zRPZWsx55LUnOLd/yN565J5LBxxOokqcWfRszyv7w8i5wzW1m3G4XLEzK7zSzWd4sZuvg9kGhwrW04SnBJvtxZyTfWEDI4mxNaI1lANuyR4dd60ak4JbtmbMi1jWBQsa/eFF3BplOCIycSmcc+G+2Pyj+1r30V/6vT/4p/zXQPwX+Pb3e6OTrOvntdJ/qEtlg4mNGrTomLqeIRMkVsPI0TAwjMm8wKXDI/7kKU/jzLFtxpac2z9iyGA1jKxaArDZV2aCrVlHQxyuR9Yt6UrwsJNbPPi6M1x/5gzzGuwUgRMbNrrKoiuUKEyq7FNgHFhMR6iN3Np67h1gO5fcXJPAHM6PE7Wj7J9jjtnSRMvk3jF4SmyxN9ti9/CAUvtvnDj8jO/4jh+7wH8uxH+y73+313tzSvlmx+zGZZkzKtjKkc2SZMw4JBgkiGBsjf2jFWMmsyoODvZ5xtkLHA2NMRvnDtaMCWSSiNFJIHByrK9ct71ge2PB1tYG2ZJjG3NmIRZdYYOJa7a22NpYQOmZorBMLhsTDtpE3yY22xqPa25vHRfWjRtK8rBjc+jmrLsNJpJuHOjamulwn9uXE7eXLfYXx1AEy0sXWa0HDg6O7nSND/6pX/zVn+c/D+I/yY++w2tvDX39EqMPbVEYS89SPROwzcQmExEdS1XWUWiCw/XAwWrF2Mw4rLiwt8etZy9xzfEd7rq4x9GUlChUib4rLNcjmUnfFx5yzSkedt0pNvqOcT2wXB5xtFozjSNdLcxK4fBgHyccP3aMja1NNFtQBFMmq5ZszHtqG5jGiSMV2nLNzfOO44s5R3VOnc2Z9z3L2RYnp0MOz93DX1xccVYdtXZkmzjc32OMSrd1jI1jpzhR9Y0PiQuf9GHf+GMH/MdD/Cf4gXd9zUdMLj83ZjxqjZhUabXHXU8RLNyYeyJKZYU4u1xz+7kL3LO7DxLzvmc1rLlwuGJIODbrOBobq6Exm83owsz7yuHRmmNbWzhH5jXY6guLWWUaG8v1QGtGAdM40dfCxqxytBrYX40oCie2Fmxvb7OxtUWT2NjaoqtBa8k0DnTLJdcUsTnr2a8Ljm1tslEr5/tNNp3khbv4y7svshc9XSkcNOP5gtn2cZIgo3DteMiLTxeeOA+/xdt/988/mf9YiP9gP/QOr/H2Lcq3jXB8nWIiICrRd9TaESEik+V6xRSVZ1zY5e/vuI+VzWpMbIFgOQygYKMvnF70TIjD5Qqr8Mgbr+XwYI+tjQW7eyvOnNjh0sE+zUlfC9kaR+sBEIEIwXIYODbvwGY5JruriZA4vTlja2PBsWM7bB87xolrrqHb2MTrFceO9jjWBuYbG1xyYRon5hEsszE28LDktgt7jLMNLrRgvbFFzDeIqDQnUSonpiU3XLiNGNa7lygf8Bk/8xs/zn8cxH+gH3uX1/kU2184SoyGyQIFpRSIgktHRjAabr37Hi6NjcfffZ6L62R0UhUgMWYyTiNdKfQleMjJTQ6HiWzJpaHx8DPHuf74FuM0MauFozEJwdlLB1w8OGJMczQ0SgRFYMy87+gFZGO0WE+Nw6GxqIVjs8JGF9xw6iQv9rCHsnHNDVCCm9oRO4wcqXJhNXL3uQucPHmGcRwYjw7ZPVpyqYkLLqwX2/Q725ToWI0j49RQJtvLXY4fnmNoASGW3fxTv/JHf/qL+I+B+A/yA+/y2l9t81ETYrAYDI6KI1BUWhSydFDnLIcVf/L3f8/eKhlasjeMHE6NWe1Yjw3JHNuYMw4jQ2sc25hz886MtLjz4h4tKjcc2+DEYsbRckWUoGWyGiamFEM2DtcTKXE4TKST4xsbLIoZx4lQYWrJpXGiAlt9YafvaDaPOL3Da73EY5ifOM0ioJ9GRicjYmyNjdmCs/uH3HHpiEOLZanM5gvqfMFBmvMXznLp0h5FBWWyWQtbMqc3FsRyj1tXjXtbfM3P//zPfzT/foh/p89+7deu15wu3574vZqTIZOlC1MpuBQUlagdqpWun3G879jbu8Sv/eXfcbCaOL61wd17BxxOpkQwprHNZl/YmvUcrNaUUjk+C244sYMNt569yNiSLoJZDSQQ0JfAiP1hZDWZdUvGZqIEmzU4uTXn3KVD+hLMu8LdhytmpdCH2O4rk8UwDrzMg27iNV/6xZhhYproi9BsDhFslOBwbFxcT0xpVqpcPFpy78ERF4eJIRtSoZfoJbZz5DqvmEkc1Y47lmsuuud4p++57vze+3/2b//2xL8d4t/hs1/7tevOtfPvazm985TJujVW08TShaw9pe9RqfRdZaPrODnvOBPm9rPn+Nm/fiJpOHN8h9vO73LURDMYAyZCnJzPkMz+amTKZLMrnNna4NSxLRa1YEARTOPIOCVH64Hd5YpVM2k4WK0ZmtmYz5gV2Oo7zu4dUmrh2Kxy9mhEmFkpzKpYjg1bVInXfZnH8goPvpFFTvQkR1Mjo7AxmzEkHAwTR+PE+eWa+1Zrxjpnio6VzTQlNRsy9DmwsdznyEFXg+uPbbB7fpcNT2zKP3x4oPf47N/+7Yl/G8S/wze925t9d8J7tWwMJMuhcTSODBTUz6j9jKpgVgvH+sLJTpzUxF/cege//JR7CAVdCS6tJ1YJLZMSQV+CkMgcObOzSWtmbzUwtiQUnJwFD7v2JKUE917c5/zRmrHBqiVTJsJs9B2LvnLhcE1XK13AvAarKTlYj8y7YH9otJZszGa01phsioIqOLOofPDrvyoVsXtwSLhR+jmzzQ2aChdXE5dGc2m15CBh1RqrwyN2j44YHPT9jK50dMMR3dEeXa1sb21y/fYM714k3JjXiqTv+fCf/u335t8G8W/0w+/5Rl+d1I9yQLMYbFZp1q2RhqgzatdRJRZFbFaxFabPNX/yjHv45afeBxGgoGUyWXRFZCbb8zldDY6GicWsY7srTAZJLGY9s65y9uIe9+zus2rQbEoENQRO+q7gTPoINuY9q/XIrO8ICQxHw0hr5ignphQJtEyKAjBFYqcLXusRD+KWMyfZnvU04FKKM9dcS1sdcc+lA/ZUuTQM7K3WjGNjOjxk92hJKZWayY4a13RiViqjBJtbaBzYXh5QamFUUEthXvmaj/mJ3/ho/vUQ/wY/8x6v9ylWfCFRsIKMYLQYHWQ2iiCiUEuhYPoCfQRVRjnxd/dc4BeffDejgRLMup4ahaNxZKOvzIrou56Lh0v2liMbs8KNJ7Y4vrnF4WrJHecucuFwwArSIEwfwaIrbPaVEsJAiWDeBRGFCDGOjWwwZmOYGkdj4+Jy4GCciAi2Zh1dCDDXbG3yyGtO8uAzJ5lvbrGaGhLszHoQnDtasZfB3mTO7x+wXq9Z5MQyC0sn6+URmzlxfNaxqnPc9SwiifWa6zVRBVkKGwEnqonSf+p7/+ivfhH/Ooh/pZ94t9d++xrxYxGVVEAERqTBCGFCUBSUEEUQBUoUpMCZPGP3Ej/5d0+n29zCaVaTmfUzLq3XYHNqa0420zKJUjmxOePYvLJcrTlcjewu1wxTUhAS9DVY9B07G3OOby2YlUrXdfRdQQR9rQzrNbsHBxwsB8bWWI0jrZmzhyvuO1qzbsmiq9x4fJPqZN51PPaak2xsbBAbW5yo4Ew822BWCnt7F7lvhH1XDoaBg9UAmYwKDpoZppGZxMym1MrJApSgDGuu9QpStBKkAtrIXQ0OHO/wA7/62z/Oiw7xr/Dj7/qajxDxpyEdL6UgCSsQwiQghACIGtQIqgIJXCqNYNUae2Pyi3/3JJYqLGY9e6vG0Bo7mxus1iNdCTqZcZrYnvdcf/IYq9WKsxf3SCeLrmPRVbY35xzf3iYi2FhscOr0ac5cex1bW9vUbk5Oa8bVivXykOXhAZfOnefC7i4X9veZEg5WK+6+dMCF5cil1Ug/69noKjfsbKA2sB4mbjh1khe7/gzM5txDjze3UHSs9i9xabnkqCXLYWC5WtFSdG1iPDpkRrJFsimhWkgFu3VODmuOdYWMyvmoTHVG5MSwXpPLw93VpQuv+Gt//fgn86JBvIi+4R1ee2uH9udd6FE1RFVBASEAgQQSUiCZUBClIImWZrBYUTgg2GvJbecuctt954jSs04YMqmlUIAuxNaiZ9ZV1CbG1ZKtxZwbrrmGG645w/HTp9jeOc7GxiaLxYI6m9H1c0rX0y82AJEtyZzIYc368JDh6ICDC+c52Nvlzrvu5r7z57nz/CV2l0uOxsaywd5qYDHr6YrY7gRp1uPEg669ljPX38jGrLKoHUMtrNYrDpdrzo1mHZVxSsajI04sL9G1icxEIZqCJYWlCvsW127OOTGfsxeVey7uYgXj4R7jlCxmHT46fOJif/nyP/a4xx3wL0O8iL78LV79G2ZVHzoLsVHFhqAEKIQtUCFCFIEEqDBJLFtyOMHSwUqFpYJVMyXMvWcv8LR7L7BKU2uhL4Vjm3M2Zh2bXU+hcWxri0c+7KE8/OGP4LobbmKxfYy6mEPpkYK0sQ2IKAJETo22WjKt10RXyWHFcHTE+uCA5f4e5++5i1tvfRpPufMezh0ccDQ2UHCwnlinqSUYx5F5EXYyOnjszTfySjefZqMW1lE4Wg9cXDWeMYpDRBsG9i8dsL3ew2lWpWNIWCcMURhbwyGuX/Qc7wrL2Rb37u7S2oTaxLhesRHwqFM7PGx79o0f/CO/+mH8yxAvgk94w1d/89rp5/ooLKrYLmZbySzAQDMQhT7ELIQEI7A/waUMLqVYEkQp9BFAkE4uXrrEred2ORgmNhc91506xawWwsmpY8d45MMexqMf++Jcf8uDmR87TnQdikJiQoFtsMlpxDaKwIYcR5gmpmEghxU5rhmOloxHh6yXR+ydvZd777mTW++8i3t3L3Hh4Ii0aQruvXRIIsacaJnMouBMFrXwqg+7iTNbG4wlOH+45p7lxKWxcTQOlARnwjjgTFpUqoJO0M3mlAhW3YzJyYn5nFUUDpdLchyJ1QFnanLzRs+Ns+DkrLAxq2/xOt/1qz/PC4f4F3z2O7zRyWG1/ttBcWMiOszMjQ01ZhKJmYCiYLMGGzUomKPJ7CZccmEVlVorx/vKjhOVwlQqT7zzHp5+7iKK4OZrT7O1WFC7nmtPneJRj3wkD3/Mi3Pi2hvoNzap8xkRgQERgHE2cprITJwNJHDC1MhpIqeRXC5p6yXTcsn6cJ9hecTe+XNcPHsfd91zF3eeO8fecsV6bAyZ3Hew5GgyYybDNIJFXwvT1DixseARN99I3xXWU8PZaNPEaj0QEhVo4wTZMMKYzMRAXyr7mycZFpv0bWRaraie2AhxmoHjpXGiLxzvK30Y2XeWaf2Sb/xjf3SBFwzxL/jyt3+9bxisD12nODSspsTZmIWpChBMNgXYLGIRICdHDQ4RrXZszObsdOJYCY4roXTsNfjTZ9zB085dYntjxqntTY5vb3HqxEke86jH8IgXe0mufdBDmW9vU+oMRYAMFkjYiTMhGzk1Mick45YoG20YyTbioyOm9ZJxtWJaLVnt77E62Gf37Dnuve9O7r7vHi4eHDImXDw45OK6sTtMrJppmbQ0IRCiROGaE8d5pZtP0wmmYcVyNTIkNCfjOLIck2FqDK2RhggRUZgsLvWbsH2cjTbSD4dsFcDJCZKdaMwLnOoLO/PKRt9Tir/xtb7z1z+MFwzxQnz7O7zuK04RfzJZrJo5TNhrMBpKgSgFRdAMYCpQDM6JIRNLLLqe47OOY1Vsl6CSrBN2G/zy3zyemG8yj8bxrQ12NjZ5xMMexku97CtwyyMfy9bJ0/QbG6hUrIJkgitaNpSJpxHb5DRBJmCcjRxG2rAijw5prTGtl7TVitXhPuuDA/YuXODi+Xu5487b2D864uzuPpOCs4crzi5HDkZjJwk4G13pSEPfBa9+42kedXqLbMnZo4Fzq8bucs1qHBnTjAj1M6iVTJMt2V+uuQRcc/IMJ+c94+qQ9WrFbL7JjVs9N7R9drrCTjWbRcy7nnlfIdsrvep3/Mqf8vwhXojveJfX+0OZV8HJlLAyrC0mgiiVWgpEYVSwBhrQmrEbyqTYLKqYl0ovkMxUKg1x38GSP33S04kSdCU4sbXBQ645xcu+zMvy2Jd+BU7deBPz7WPU2QJKpUQBDBLOBDdybOTUsCdymoBECc5kmkbasMarFW1Y0Y6OaOPA6vCAcVyz3N/n0rl7ue/uO9jb3+f83gG7h4fsj8nte0dcWCeTwU6EqaWQFrUE1yxmvMIt11BJ7llOnBshZ3MuXLrEwWqkLuao6+j6OQAkLI8OWA8TpxczTveVfYuj0lGcbCu5piQ7jNy8teDarRndtILW2Jz1f/Ra3/Urr8rzh3gBvvmd3vhtC9NPyI0iE4aGmAAkIiqlFByFMSpDVEZE2mROTONEuAEAQVOQUXApzGrl9rPneeo9Zzk4XDLrCmd2FrzUwx/Ka7/O6/OgR78YWydPE/2M0s1QCFQBEICA1shxpLVG5gTTRLqBDdNEtqRNI7la0dZLpvUKTxPrg32m9Zr1esXBpQucveM21usVR8slewf7nD9Y8rSLl7jzcGRvnWSaEhASfa2kYAbceOYUx48fY+wXHAwjY0v2D45YTyM5DgAUQAoMRASLxSbXndhmMY2MCi6OSZVZ7e8x7yuLHDnWd5yOxi2blVPznpOzjq3Z7O0e83U//pM8L8TzYdC3vPPrP05TPlokgRGJJBIREgoREbToaKVjio4RmFpjGEbGbDRERsHR4a6i2jGrlTnmSc+4nXv3D7n9vnPMu8ojrzvFm7/+6/KKr/m67FxzHd1sQdQORYEQig4wOBECmzauyEw8jeQ04TTYOBs5TmQ2GAbWB/vYSU4T49Eh0/KQ1eE+q/XA4e55ds+fZbVaMq7XDG3i6fed5/FnL3HP4cDeMBESRWLRVSzRl0LXz7jpxhsJzO7eAQfLI2iJMH0JKqKEwCYxJRNtbnN8e5OtNjK15GKD6GecqLA5HlEDZrMFnUei67lhFtzUmb7EE17p237hsQLznBDPxze9/eu9c5I/1DJxJmljgQgIAUKAEZNERmFSMBlaJquEEVDtiG5GN9tg1ldmXUdxEm3kKbffzp0X9rjtvgscX/S82os/ird+27fnQY96DIvNLUo3I2qFUigKUgE2kAggkxxHWktoI25JjiNIgGnTRKZhHGjDmjaNTMOKtloxrY4YDg9YrweG5QHL/UvsX7rI+vCI9bjivouX+Nu7z3Fu1bhz74hVMyWCPmDRVRQVkTzs2jOcmBUOlmt2VwNC9GFk4ZbYBoEwEKxmG2xsb3CyBLNMzh4cclhmLLrCdbNgh0bniWBiVOHFTx/junllViullHd57Ff9yA/znBDPx1e+9Wv97eh8iSEhDQ2RCEtYghJgaE4MNIuUaIYEHJWoldlszqLvWPQzNrpCJ1iPI+tx4I6z5zi7u88Tb7+bR91wDa/9Ci/Da7zRm3H9Tbcw39wgSkfUCgok4SiAkU0bB6IUPCUtG7leQ5to00iUihHOJFuDqdGmNW1YM61XTKsVbVwzrpaMqxXrowOG5SGrvYssDw7Y273IwXLFk85d5NYL+1xYN84eDYw2VXB83jMRVCWPOrXDI04dZ/dozcXVmlUzahM22JAKwDiTweJwtsH2xowziw02u8rewT6rZqJNzMKcXnSc7IPtSLZLcGZjxsmNBQVzoPJ3r/z1P/6SPCfEc/nit3qNNxodv7xOmIAGJMIELQJKECVQQnMj0xgQEKVQo9CXStdXZqUwL8EsRCHJ1jhs5tIwcPHgiOU48Q9PfQav+KgH89iHP4zXerO34bobbmI2mxNdhyJQqUiBIkhAmQDYJqcks+H1EePBHm2Y6Da3US201nAmTBNtWNHWK6ZxzbgaGIc1bRgY1ium9ZJpfchqb5fVpUvs757ncLnknv1DnnD3Bc6uRi6sG3vrkQQ2ukpXClXmMaeP8fDTxzlarthbjxymUBvJNFOao4RlmqklY+lYR+H05pwTXcfGxgYXL14kskE2trtgZ1YZ0twwDx65WdnsKyHRFPzDxSX3TOWNv/AXfutXeDbEc/n8t37dX5jwm04WECgEEgm4FBSFrgShwE6cDRFEiBpQIgigGUQSTsKNTNMI1iocTQ1HcOd9Z7n1nrO8wsNv5sUe9Uhe/Y3ehutuvokahdrPcAiiENHhAElgQybOxK3RxpEcBmgD05RQKqUU2jRiEq0bw3KfYbWitYlhvWJ1dMj+xUuslkfYpgjKsGJ16TyHu+c5ONxn92jN0y/s8+Tz++xNjeWU7A8TtQSbXaUquOXENjcc26Stl7SpMRI4Tctk2ZJLk1nXOVMp0FWGoyNOby44vrnBdHjItDqiDzHres4sOgagzjd5sY3kullhXgp9EU3iiRcPOH3yml98y2/+kTfj2RAP8Plv+7oPCuvpGRKIApQASRiREqUUuihUkssEkogQAE6zbMnRNDEabGGS1owj6GqlYrq+8vdPv51LRysee9M1vOzLvCwv82qvw/U33kztOqJ2uFSiVBQFSuEyC2gwDeQw0qaRHCcAsjWyGQE4yeGIXI8MR/tcOH+Ov/i7v+cpt93OcrXinnPnOVyPZDa6EC/24AfzEjdfRzncY//SOZbrkYurNX9z13nuXE6MhqOpsWrJsa7SBdy4s8XNxzdp00gbk+XUWLfGOsVhmgMKretoQDPkMHL9sQWntraYDo+YTWsolZgvCCfLOuf67QW3sOSa0uidzPtK6TueOM0Y68LXHFs85N2+4juewRWIB/jCt3qdz0zpc1QCSQiwjW1aGgMlRJUoYUoUSilEKRhohmFsHLWJozEZga4UuiIEzCLoBNisPfE3T7udjc1NHnr6OC/1ki/Ni7/Sq3HtDTfTzxeo9qhWVApEQFQQyMbTiMcBDwM5jWSCotBa0tYrnA2mNdPhAevDAy7ceze/+Nu/zZ8+/skcNDNNE4pCF0KYRa0UwXbf8UoPfzCbDCxXS9Zj4ykX9viHc/tcHBIrWE0TW33HvMAjTh7jQTsbLMeR/dXIYUumZg4b7KVpXU8TTC1pwEzByXlle3MLLMblERZovsF6XNNLnOng+nnh4ZuVrQJzkiMHjzuCWGxx4/bis979m37gc7kC8QBf9Fav9YRGPEohLNFsMpOpNVqatBEiAqpEqYVSKqoVA7ZxmiQZE1Awr4WNGhSMMhlaYyQ4GNf83dNu55brz3Dt9oJHPuLRvNxrvgFnrruebrFF9DOi67AqduKcODw44N677mT37H3EOHB8a5Nrr7uOfnMbSodKoa3XDAeHtNUh6wvn2L1wH3/7V3/OXz/xSRCFdSalq2wt5pzY3qGvHTWCcRq578IFlgdLHnrNSUpOtDZxYbnmcef2ecKFQ5oCY2alsCjixc6c4KbNjuXUuLAcOFg39lqy74DFBhGVycl6GLFgIXFyXuj7OSXNOI3srgdMYbuaWzYqD150HJsFizBdBH2Ie73gbL/Fdl957Lae+Hpf8X2P5grEM33Bm7/GyyL+ogmkQo1AGAOZjWlK0oYIJFAEUYJQhRLYEEARFJkxzdRMCdjoOkJinEaOKIyI5XrFE2+9jUfccj1bnXjUo16CV3+jN2Vjc4vZ1g51sQW1Zzw65CmP/wd+9Vd/hSc9+Sksj47AyYYapzY3eI1XeVVe7jVfh60z11HnC8bVmmF/n+XFsxzedzcX7rmdu25/Gqv1ChDzrW3m2ztcOlyxXA2M6zVVZt5XmBq7l/Y4e/4C1x7bprXGuo3cdjDwJ3ee52BMZrViw0YXPPTYBi957QmOhoFzRyP765FzY3JQOspsgSSmNrEeJ5CorXHTsQWyWTe4uH8AErdsb3D9DHZqsFXg+KJnpy90Ifbc8fSlYWuH4wVe6tQm28Pwci/11d//lwDimT7/zV/98xJ9ugUlgj5ED0QANjYkgIKQaDJGWEGTMAKLIEFiaGadDSNqKVgwTclgE7Xn8OiQsxfO8dBrT5Jt4mVe7pV4zdd7Y2aLBXW+Sbe5w9HBLr/2Mz/N7/7e77G/XIENbWSrDx52w7U8+sEP4aabb+bahz+W7WtvoO4cp02N9e4u+3fdzsXbn849z3gy586dJWnQ9XQbx1mleMIdd3PHfecBc2pzznVbM07OOo4tFgzjwDgMLNcDY2ucW635o9vPcd9yYmvWMbakK8HJvvAy158iW2NvGNlbj1wa4aj2xHzBMAwM48TUGgFsCG4+c4JcHXGUwfn1SKfguu05J/rKIieu3+g5Nu/YqjBFx+MurVlHRRFcvzXjFU5ucm3l8x/5Zd/3GQDimb7orV7zLyfrZdJcFjIVCExISMKAJFAwYRJhgRU0Q0toNg2Y0ozZEFBL0NVCr0IXpisdd1/aY7lecmKjculgxeu+1uvy6q/3hnR9T5ltIOBXfuYn+OM//iMWXcfOzhanjm1zfHODY5sbnDq2zbFjJ9g8for+5Gm646ep2yewCutLu+zd9nTu/Lu/4olP+nvO7x9Qa6Uutui2j/N7f/8knnFxn9V6SZUomBOLnocc2+RR15zg+MaMcRhYrQfGllxYrvnjO89x19HE5qzDmUyGOcnL3XI9NRvLceRgGDkYGysKq6hMCEowjRN9Josijh8/xrQ8YjUlSwXzfk6dzalhri+NMwVmBVZp7lwDmzvUWnnEsQ0ePIOHzhobtf7VI77k+14WQABf+qavfV2refeEGNO0TAwEUASSAGGMEZZIBBIoqVFICyQMpI0lhBGmL4VFLWyXwmaFkHjapQP2xhU5DpzfW/MWb/iGvPrrvgGqldr1PO1xf88f/95vc8stD+JBD3owpUBOEwf7B+xduMD5e+9hYzHjoQ95KMdvvJmNa65nfvIaYrHFcHjIpac+maf+2e/zl3/3N9y3f8SZa65he3uLZxwl+90GZ8+f5ylPeQpziQfdeB133nknkY1Xfch1PPzMCapNS7Ner7mwGvjj289y++HAvK9UzHJsFOAVH3Qdp2cd+6sl++PI0dBYjo2DhFU3Z8IwJTNM18/Z2ZgROdHGCWwKImYL5iU5Hslymrg4JGsVYmObzY0NNqp49EbhEXPR1yAi2JnPr3/FL/vuewTwBW/5Gu8s4ocakE4wGCGgACEhiYZJIG1CQZGoJSiCCBGCQFjQLCYnQvSlstkFO10wk2kR3H40cmlYcve5C5zbW/Fub/u2vMqrvyYEHB3s88S//mu2Nre58SEPYRpHbr/zLp56253cd2GXo4N9NrvClsyDbzjDLQ95GCduuonN626mbp9gGkYuPe0pPPmPfoc//Ye/Y3c5cstNN/DUO+/hxV77Tbjr/Hl+59d+kdU4srO5zaNuvpF77ngGB6uBh5zc4aVvuZat+QzSLJcrdpcr/uyO+3jKpRUqwbwW9lYDgXnYyR0eeWoHu3E4TFxajRwOE4ctWdUZqYBxpJPoauG6rRnVZnc90eWIbPYo7DdwJlErW1ubzGdzun5G6SrbXeGGeccNZ05z/fac42psrvfe5aU+79t+WACf/+av9k2WPrgZsJFNkehqoZPoQghjRAMSECBEhABRaqWEKJgJMaQZESgIiXkRG2EkMSacG5KRkbvvu5dze2ve5S3fild5rddEtXLxvvvoSsfmfM7y4BJ//eSn8st/8Gfccc9ZDtYT07jmpuuv5zEnF7zkDWe46eGP4sT1N7A4cz2LU9fQhpFLtz2DW//ij/jrx/0DU+nY2NhgSeX4mWtYrVfcefc9HBzs04Y10QYik615z0Ovv5btxYz5bAatcXR4wPndS/zNvRd5/IVD1mm2+o691UA6uWlng8dcc5wcB/bWAwdD46iZgwxa7VAmPY2KCcOpzTkCdlugWllPjaNpovYdSui6SikFCSIKO8dP0NdKZONBxzZ4yVObnJh1LHL85lf4vG/6EAF84Zu9yl+k4mUnB2mTbhQFXYgaUIAAwNiQEhEFBEZYFRchiQI0YEpIRAoEdCH6YooqBg4aDNOKvb2LXDxY8xZv+Ma86mu/DtH35NTogHH/An/z93/Pt/3srzPVGVtb23QbWzzp8Y/jwQ95KK/3Mo+hO3cPL/sqr8rJG25iqjM2j5+krQf2772Hu/7uz3nik57IXooTp6+BqJQi5rXQhhWrwz2G1ZJhGNiYz9mab7C5uUHtesZxINrI0cEB9507xz+c3eVv7ttlnbDoKnvLNcY86Pg2j77mOHJj73DJ7mrgYDLL6GgRqE10MkViXjuOzwolJ86ukoOorFpDCopAiJZJkTi2s83O1jZjJlEqXYidjQ1OH9+hb2sesqh/+S5f+W0vp699kzeZjXVvbzL9hBgTxkyQCCBkiqAAkAQBEhEFAhIxEqRESBQgBBFBkZACMCERglqC5mTZROsrF87ezdF64jVe5TV5zdd/Q+rGBjJoGji47y6+7Yd+jL956u2807u+G3/1t3/DP/zt36LoeNQtN/LqL/vSPPhBD+bUDTfRbSyI0jGfz2hTsrp4gXv+7i956uMfxzIK2jpG6ed0s56+dixmlVkRnkYQOJOCQEKGXC8Zloes9/c5e/Y+nnxhjz++4z6WDWoNjtYDIfHI68/w4FPHkBt7+wfsrwYuDY1LzTQCZ2NeC/MSRC3slMK1M3FxOfC0o2R/GJnNZohGVztam+iiUkswn8/oZnM2N7eYppHFbM7m9jbHtjaZDavheHfnjr7qTV/1pR381ShIAwqaRRrASBCYAhRMRCCAKKgIIyaEJWQhoCoJQUgYQIGiIkwqGLOxssiuI9cHXNrf5zGPeQne9C3fjm5jE0kUJ+fuuI1v+fZvZ3M255ZHPBrXjvvuvofTx7a56cwpTlxzHTvX3ki3s8Nsa5NF7QhDtsZ0dMS5Jz+Bp/3NX3I0NmJjg7q1Q93cYrbYpHYdIVGLMIZMSpugTRRMro5Y7l3iaPci587exx17+/zOrfew1yAM6cb25haPfsjNLGowrFasDg8Z10ccNbE/NNYSaRBCTow5Oe85XuG+/RUXKAyZCFEjACMJpol5DU6dOMF8Y4NhGJltbUEUcmrMu2BcrthazF5GX/6mr/IuDf9gU4ChBIQEBAmACUEgaghxhaKQEhOQGCNsA4CEbRKwAiIAkYamYLKZbKIUekZWqyU33HAzb/tO78F8e4colSCZDg+49847We5fxA1qV5GTWju67RPU7RO49nTb28xmM2o2PKyYVgPjcsmlu+/knqc/hbN330WZ9ZTFJhtnrqMuNpjPFtTZDLdEBTyOlNbwNKJs5PKA1d4l9i9e4PyF+7j30gG/devdnBuNsnG8r5w8cYKTZ07jTNbDQN8GpvWaqU2sGxy1xqRgOUw0m/U4sdH31BD7Y6P2Pa1NOI2ArdmMra7QyVw7r1wz7+hCjP2ce13Zc2E2mxFAmxrzjcW76kvf5JU+c5Q+p1kYIUwARYIIJBNASIQEQEqkxWCYAEsYSMTkRkuYDCiopTCrhb6IAKxCRMGY9TTQdZVCstjc5h3e9X3YOH6COt9AmbRpImrFOeL1imwNSWR0NCrNkKXQL2YUQG1ivXuRthpZHx2x2t9j985buevWpzEMI/OtLTZOX8v85Bn62YxSKxEBNmqNyIlcr8lhTVsdsTra52D3POfPn+O+S/v89jPu5d510tmc6MSJnW12zpwhnTBNqK1Zjwk5sZqSdUtam0gFpS9MCQdDMqSJUph1PW2awKZkcsOicN28Uruezb5w/aLj5Kxy+1R4ylqsZ5tYIkqh7zq2t7Y+S1/yJq/wnUl9n0mFVZrJSQCzIqogJIqCIqgCBImYXFjbNGA0pERimkUDbNOXYLMWtrrKooguoIsgSpCGew6OWJeOjVlhY7HBG7zVO3Hy2hvptrZAIm2iFISwDTYtzTQlmYYS1FqpEmoTOQ4Mh0dMLRmHgenokP2nP4mzt9/KvXfdwXx7h83T17I4dYbF1g4RHSEoJM7EwxoPS9pqybhcsl7uc3Swz/lLF7lnd58/vO0+7lwObIY43ReObW6ydfI4R9PEHLFuyXoamMaJIZNSK30XHK0GhmEkarDK4NLQqCqUEsxJNgt0UTlezfGucGzesVkLJxY9yzSPn+ZcKj21n5M2i8UGNywKp0r7Ln3xm7zSr0aUNxgJBsPkBmlmEfQh+gK9gi6gSCBAhQEx2AzNTIiUSCARBjKTPoKNvrBRK4siZkVUCUI0JxeWI3euRhaLGaeOn+BVX//Nuf7mB9Nv70AJFAVJmCtyMraRRKZBECoUEpFMR4fkNEFUpuWSvbvvZH3f3dz15H/g3rvvZojKtQ96CDvX3kC/sUMphRqBJMiJXC+ZDveZjo4Y1kesV0esj464uL/L3Rd3+ZM7z3H30cS1s8J2EVtbWxw7vsPuemJt2F8NjMOKaZpAYtEV1FWWQ2M+m1H7yvmDFZcO13S10EVwoguOl2ReKicqbFWxUcS871jUwh2r5K+nOdvHjgHQDKc2N3iZbXEd61/Tl73xK/01tb7UhDBBulGczCLowvQRdIIaokSAxGSxslkmrG2ahSOQhBCWkEwv0UVQQsxCzKroIwiJxKxb8uQLe9StbbY3t3m113kjHvKIRzPb2UGlolIBkwYMTjBGIZRgjBSIRnWyurQL0witMR7sc/H2Z3DvM57C0299GtuzGbaYZlvc+MjHsLF9HIUIgyKgTbTVIePhAeuDA4b1AcNyxXpYs3+4z927F/mTO86zPyYP3ehxJhunT3H82Ba7Ryvu3DvicL0mIhiGiak1TGLE1IxCYFjbNMS8dnSlsAhxujSOVbFVK8dnlUUNSi3sTeJvL60Yto6zmC9QBLVWrimNV9ypXLfo/kZf+savfLtKuclFgAhDBxQZY0BEiCJRMEKMCvYtDloyAiAiRFEQCMnUCLoQRYEEgdmowawGXRSwsc3u2Dg7NY4dO85Lv9yr8JiXfGkWO8dRPydKxQAS2LgZCyQhGyMQFAHrFT68xOHFC7Q2sT5/joOz9/Brv/Wb/MbfP4XXfMnH8AoPvp47Lhzw4Jd4WXZOnaYocJrWGmoT0/KAcbVktb/H+mif9XrFMA4cLg+5Z3ePf7j3ImNLbtycUyLorrmWE2dOcN/5Xc5dOmTVEpfgwsVdVsPEujWidExjo7WJDEEENvSl0PcdVeKYGn0UNotQCAnWU7KvihbbzDY2WMzmtPWKMyeP8+LH5jy0mzjV1zv0ZW/6yrsR5RglECKcCEjECDRVLnNSZApiQFxKcZRmAhRQIgggbEhTQ/QlCImIQBKzGsxK0EuQDQGLxQYHCRniQQ99JC//aq/F5olT1PkGpXYQAYAzIY1LoAQwRtiNkGB1iO67jW/96q/ivil4v3d+B9bn7+OP/vAP+Os7z3Jsa5PXe4mH85Rn3MUjX/aVOHHdDdSo5DiSbaKtVwzLI6Zhzepgj/XqkNVyyXpYs1wvue/SPrdfOqALsX+45sYTO2hrm+PHN1mtVuwv1+wOjXNDcrBas1qPrFtDBOTEib7n3OGSpQIJohb60iGANlFKoQJjS1QLUrCxucnOznG2trc4UcWZCqtp4sZF5XQkvbikr3yzVx1KrR0CGSBpCQNi6WBQMKZJmyJTxGWHFNYWo42dhAADNsIIUUOUUohS6Gqhr5VOMMNompDNa77iK3P9TTfzO3/8e/TzDV7xNV+fEzfcxGxji9JVJGGDAREoAgBjnEZp0hNeHqB7n8Hj/uxP8InrefiDbuHirU/ivrvu4PzuPsO45vz5s2zsnOKhj34sO6evoczm5HqgrQfGcc2wXDKtl6wP9lguD1ktl6zWa9bjmotHS+7ZP+TC/iF7y4mHnzrOsdMn2NqawbBmOSX3LCfuPho4GiemNjEabBE5sYm5uBq56IBMkJj1HYGQwYJaCqFAIeazGV3XI4lZX3noZsdDZ+LY1hZbmws6jIZh1Ne91atnlE62IQ0kg5OlC0cORsNgM7SGBUUiJFZpJkSzsE0EFIsIYxshuoCuVOqsp6+VvnZIpstGjAMbEi923Rl2Tl/HcjbjKbc9jZd+pdfkpoc/ksX2MWo/BwlJgCAClSAtBLhNOBNnw+sV0313kcsj6rGTRJiDO5/Bcrnk4r13c+etz2BCnLn2ejaOnaDOZ5TZAgHD4SHDek2OI+vlEavDPVaH+xyt1wzDwDiN7C1X3LN/xPn9I47WyfU7G5w6c4L+2Dbj4QFH64mL65Gzq4HRxjarcWJqJgTroyX7o2mlAklfKrVWABQiSmHW99RSWR0d0fczZrM5XVfZ3trgpXZ6HjQL1M2ZdcFi1jOlrW96+9dNBcpsZDPZGusUy4QVAMGYjWUzCdQIHIV1MykjiU5BF1BCVJmC6CRmJagliK4nSqUrQojipMuJavPgkye49sw1zG98EL/2x7/Ho1/yZXnoY16cYyfPUBYbKCqSAIEEtSCEE0xiEk8N0kzDCk8TpesIN5bn7iUFB3ffyYW77yIVlG4GQImAKERU2rBkfbjE08RqecDq6IDV4SGrYcU0TqynkeV64O79Q5argfmsZxxGhsUm48YmVWY9ThwsVxysR5bDyDhOqBTSkK0xtsbUTEM4RF8LgVCIbBOzfkatlVo7pmlCKuwc28aIR+5s8Mo7QV+DI8PYjFsjwfqmd36DISK6NgxM08TQGssUQ4pRoghaa0wGI/oSRIhmMCIimNWgC9GVoGCKRC8xr4VSglSQCkqISpBu9IIaYmtrh0c+6GFsXH8zf/R3f0nMZjzmpV6Ok9dcS7+5Tak9CCIqRIACSRhAkJlkNkCAIROAXC85PHsvTjMd7HPpvrtZr9YkAIaEqAWpQE6s9w+ZhhXjes2wOmR/f4/1eo1tpmwMw8hdlw5AMFmMNvvRsTclcjJkMkzJkI3VMOJmDAwtaTaZYIxDFGAeIiWMaE4g6Gqh1o75fME0TRzb2GDWd5zemPGyO5V5EUfRc/rYDjMamR71te/0RrsROuZpZBxHllPjqJmVA6vQReBsJEkfYrME8yIiBIiIQleDLoIQYEBQZboSIDGlmBBFUBQYKCH6EpTa88iHP4ZTNz6YJQN/9md/wqNf9hU5c8ONLLZ2qP0chaB0RKkoAiSQQIExzqRhMHiaGNdHaBhYX7hArtYMexc5OH+W9fKIlY36nmxJlEJEUBDrowOGoyPaNDKslxweHrBerUhAiPU4cNfuPucOV6wQ15w4xpDJucM1E6blxHo0++PEepjACYIpIQ1GpGDWz1go2SQxgUM4k5UKkgiJbr6gCGYSddZzNCU3bs45seg5fuw4pzbnHFvM6brukr7wbV/v9irdJCdTaxwNE4fAkkBUagichM1mCXY6sVXFRgmKwBEoCgqRFi3NOhMEAdimAWOaNEgiJapEF6KW4Prrb+IVXv5V2NmYcfddtzMcO83W8WMsNjaZLbYgKtRKdD0RAVEIiWwTlArA1CbSSawHtL/L4d13szx/loNz93Hrk57Ecn1EKKgbG2yeOkVdLKCbUbqOADyODEeHjMOa1fKI9WrJarmEEBGF5XrFPXsH3HYwcOzUcc6URMC6JQIurQbOHa64tBqYEsbWQOJoatgAoimIWtmcdWzTmEWlU9IDWTomTCcxm/Vs9D1Dqdx58RKuPep6usUGxXDjiR1uPnWcWusd+vQ3e42/LqGXspMpzarBymJQAQUhETJzYKOKY53YKmJRRA1hBY5KAlPCckoOMhla0lribEyYluAIQGQEQnRhFn3H5sYGb/Lar8eD5x2X9vbQzQ9ilJjPN5gtNohuBrUQXU+JDkKoFAAM5DQyZVLHkd3H/Q13/93fMB4dcPH8OYZx5OzuLpRgWK+RCovZjFOnTlOO7bBx/DizxYJxuWZcLRlWK4b1itV6ybhao1KIEMv1irN7B9w1Bjcen3OCibXF4diYMrm4GriwmtgfBlajWQ0TkKREGhqipbGC645vs7E+Yh5iFkEpQiFKFBal0IVYVOHac27dGDFttkHWGUwTJ3a26GcLrrvmzN/ok97glX+V0BsYMSLWhrWhKUBBVTAL2Cpio4qNEswDOoElmqERjJihwTIbBylWU2NqjdYSGwihUigRdLUCUCRmfcdiPuN1X/lVeNkz13DhwkVmN93EUMTW1hal64huDl2hlJ4olXEamC02QSKdZGtEG7nvr/6MP/zpn6BlcsOjH8X1j3w0R4cHqBRyGnnCEx4PzTz1iU9ms5sxn1U2ThzjsY95DG2aGA6PWO4fMAxrVqsl0zRSohAhDpZHnN8/5NDiQTs9XQnuHuDs2hwMA7tHK1ZjY2yNYRhxa1SBBMJgmAxZO64/sU3u7TOPYFaCrkCtlS6CRVeZdYWNEmzNempfKQpGBbst2BsmLq1GPN+CWf9r+qTXf4XvTMX7NIJRwYSZDKODlJiVylYVO12wWYKuCCEyzao1Vi0ZDc1mNAzA6GC0GVqSrVEUzEqh74JZBIuu0pUAIEphY9bx6Ic/kld+7EuynBqz0ycZc2K+mFNrD7VSaoXaU7oORQEFErglHpcc3XU7v/E938Gt997Hm73X+7J98y2cvOEm9u65mwv33M3q4kVue+KTGI+OePLTbuW+3T3ms55HP+YRPOaht6BMlgcHDIdLlstDVqslLRtCCDhcHnL+cMW8r1y7vcEdy4Gn7Q/sNWNgHCfaNJLDwLheUyUEVEEJ6FVwBG0xZ7MGq+WI+jkyyBOo4Gx0fUcphRMFTsw7tvqKVNiokHVGKOgXc25fNu45Wn+XPun1Xukzm/w5LQKpgILRsEqzRsxLYWdW2aqFeQmKhJ0sW7I/jByME2NCWrgIFEhiMkytUSQ2S3CyD7a7yqLArIg+hAxgZlHY2dnipV/99elOnGbnmms4OtjHQD+fo1Kh64moqKuoVACEYb3i8I6n8ne/99v8/h/9Kace/Ehe7/XekHZwRDtcwrDC6zXTemBYLjncv8jZi5c4GFdkKVx/8/Vsbs2JrmNcrZhWa46ODhnHkWmacAKYw9WSc0dHtDpjqD3nh5FhvUbjwCLMzMk4NYapscpkmTCkGBERhYpYY6KrnJoVhv0DogRVQdf3TBTAbBaxNevYmfdsz2ccn1VOLTpKBF2ITkGthdlig1LKZ+mjX/cV38XiBxVBLQWiMCWs0qwQs1rY6Ts2u0IfEAg7ORwmLqwGDqZGM1igqCiCIpjSZCaLUjiz6Lh2XjhWg7lMFdQQBQjBLIJ5DerOKbYf8miO3/IQ5osNWgkWm1tEBKo9lA7VgiSkwJhcHbB721P5rV/5DTY3j/Hohz6CYxvbRIiYGjktWR8cst7f4+jSBc7ddw+7y0Ncg7KxwWJzk6iF0lXWqzVtGBjWK1pOTFPSWiPTHCyXnD88Yr69TYvABo8rYppwS8Y2sTdOHLRgbbM3NYaETKMIsJmmpOt7bjmxSe7uUkowK0FXCurmtFJZ1KCrlWPzntOLjvnmNpuzjtLNCJLIZNEVqsDj6l31oa/9Ci9t8VelFPquUqIwGVYJg4K+BDtdZaOKKiPD1CYOxmR3PXHUGolQBCiotVIDlCZstvvCtRs9Z/rCZpiKqUAIFKIvwbwEXQmkQm4eY3b9g+mPnWTzmms5fuo00VWi9FAqikAKpMAyOa2RhafG+uJFhksX0WrAqyPy6JDV4SXW+wccHlxiPQ40QdYgS8UErU1MrRGlsh7WtGFgmgZaQrZkPQxMrXFpueRgGHnsTdfRe2TI5GgYOVgn58fGufXI3thYjWYc1qzHEaWxE4BewQQ0BQ89sUkd19RSCAVTv8HQz6Gbs7lYsDOvnPBIt7nD3nybWjtivkFEkKsDioDlIbPV0cvoI97k4bPl0fG9+WzWz/sehWiGdYOmYFaDrRoswhQAJ0Oag8nsDxNDaySiCYjCop+xWaFX0JNsdoWTs8JWCWYyVaKEEKKEqCHmtVAFjkKrM6bZButuwYkHPZSHPOKR1FqJ2ZzoeqJ2gJCEMdlGpIIslCNeHTHuXaIdHjAeXGK1v8u0XjOMa1w7hmFgXI+Mw8g4rjlaHtFaI6IyjhPTsKSNI81iGEcOliuGaeLC0ZrZ1hYPv+EMZVqzKnPOHi6589I+Fw4OyUzCSa4HMk0DhmEgDRGiUzApmErldB/EuGbRz1AEq36TIxW6vmN7a4e+72FcM3ZzhtrTdT2bW9tszXt2do5xdOkC2r13eGxs7QjgA173lf5iY7542b6rlAjSyboZK+iKWATMgCJjw2Q4QqynpGUj04yGSYV513FsVtiuhZnMLGCjBH2ICCEEgBBdwKyYWQS1FFwqresZ64ypm9EdO8VjXuKl2N7YwF3HbGMLRQEJCWyTQFHglignPA20caAtD2nLI9b7e7Q2ktOEFEzDmqPDQ6b1yNHBHoeH+4zDiBFtmhjWK8ZhTWvmaL3m0tGSS+uB/QyOX3s9iy5IJ1Eqh5d22Ts8oq2OmBdwwuEwMaSZEKs0I0E6cQPVCiFmTopg1s2IEthB6ToI0aLg2nO4GlBXoDWOHzvGLcc2uG7esTmfcbyKaxfdX778Z3/dywngg97g1b5pc2P+wbOupwrGcWI1NTKCUoKKKTYFKCVQBBkVA27J1CbWU2OVEKVjoxNbpTALMwuoEUiiAQ2RhhJio4jjXbBVC30tuHa02jN0PWMU3C94+CMfyY3XX0+3sU3t50QpICEniYFAITwOeBqRjdNAksOAp0bLxC2ZhjWr/Usc7h+Q08Dh7gWODvYZViumaWK9WjEOa1brFcOUXDw84vzhiqWDWCzY2tygOJl5YqckMY20hJYT+8uB+1YjlybIKLRSWbVk3ZK0GcfGmGYeUCUyKvP5jI2+x3VOmfXkOHC0WpHLI44X6GY97uZcs7XgYSe3uW5zzrWbM47VYHu2+OabPu2rPkQAH/bGr/HOG/PZD/VdxZmsx5FhSlp0IBGCQIRMX4JZKXRdT4QIEk8TR8PI4dQYHZSATqICfYCBhhiBERESs67jeF841VeO94XNrlBqz9R1jLVnqB3ZbbJ97DiPechNbB07wWy+Qek7FAXbAKSEnIRMTg3SqFamqZGT6eYz2jjRhiXDwQHLS5dYL5esjvYY9vdY7u+xXh6xWh6xWi1ZrpZcOjjkYN04WK3Zns84feYMhFjkGmWjtAFlY2xmyuRoMhfG5M7lxIUGLoWxNY5Wa5bDBNmgmcMGx/rCrKssVdiYbzCrhQGRmcxKkDbVySNOHufU9gar2Ywbjp1gZ9Fz2itOVdjwxGap73LjZ37DDwvgQ9/0ta/bKLo7QkyGYZxYZ8NUKAUikERIdFGYFdjsO+ZdpZOQG+thYLUemZwEIAtsmsSqTawsRgKH6LoZG7OOY7OOk11wugu2+koplexmeDZnWBxjb+sazt13L2/+so9ie2PObL5B7XtK3yMBETgqkUIloIg0iAJRuCzNtF7R1kum1SHrvT1Wuxc4uLTH+nCf1dEBRwd7HB7sc3R0xOFqzf5q4N6jFef3l7zsLdfxsBObIMM0gc3YGkOapcXF0ZwbknNT42BoTJnYjdXBEW0cmaakOQlgOZnFrEcSRLCohc6mCLa7YKvvmc16uvmCzY0F/dY221vbXDOrnO7MRoHFfME8G6xX1z/ks7/xHvFMH/Umr/GXhpeZDENLxmzggFJQCVQqUlAi6EJslMLGrGMx6ygK2jQxDmtKa8zVCBvZTDbrNMsUYxQGBVk7+r5nZzHnWIFTRWz3HV1XUdfhrZMcnnkov/M3/8CT//pP+NpP/zg2CuR6Tdf3dLM5pe+I0qNSIILSdaACUSAKioIzYZoYj/bJ9YppWDMc7LO8eIH9C+c52rvE0cEe+/t77O3vs79acnE5cu/+IZeWa+4+XLNO8XqPuoUXv+4EtImJwkqFVZpLk7nvcMneMEIEUxsZDvbxMNCGCWzGZhpJHwESJigSiyp6iVkpdCVAotTKqS7Y6Cul76mbO2xu73C8E8eq2J51zLuevta/evinfMXLAohn+pDXf+XPS/TpEzA2YxshIkREgVqxREqEgq4WNvqezXnPrOtBRi3ZyJGdHOk8ETZgmmEEpigcuHCojtbPmS/mbAg2SY71la2uUjY2aTe/BH/41Nv41V/5BRbFfOPnfDIPvvF69s/ey+GF85QSLDa26DY2idmciKDWGdQKKqh2GCGAccV0eMC0PGJcrZiWhxzuXuDw4gUO9/bYvXiBc5d2Obd/yMXlmnsu7bMcBlDwjL0l50Z40OmTvOrDb+HU5oxBBQTTes1BwroU1uNIG9awPGDau0SOE2PCZNMUDBJtMjkOzPqeqZlesDGf0/WVzVrYDNEXsb2xgZzMt4/hxQbbTGwX0fc9xzc3mW/tsNhYfP6jP/zTPwNAPNMHvu4rv+xk/4UljAmgEpQQEYEVTIYmkQpcCrVWNmYzNhYzZrMZvcR2ThzPNfM2oJwoGAGSscQqevbpOKo91BkGqpONrnB8Pqfc+Eiengt+/Me+n3Pnz3NqZ5uv+tSP4jGPeBTRRlZ7F7h4711M6xV917PYOUGZz+i6OWW2IGqlJXT9HLKRqyOGg31WB3t4mphWS1b7l7h4371cPH+Bu8+f5+zBEWePjrjv0gFDG5kpWKZ5+qUj9uk4trnJw66/loec3qGLYLsr0PWsSkeWwnh0iencvfTDkmm95mA1cUQwRuXIsJwSDyM5DGzMeuYbm3S1Y0JMITws2bbZrqLrKvPFJjubG/Rb22zt7HBNJ2K2wcassjGb0fcbL/dSH/6JfwkgHuD9XvdVnoB4VAj6CGYh+hBSkJgxYcJMLjSJFoXaz9jc3GBzMWezKxyTOTatWLQ1NSfCiUiEKYhWK2t1rNThKKQhgagFzjyY6ZYX5yd/6sd46lOfxNF6xcmdHb7k4z6El32Jl6SGyDZAG7h0z92s9y7RWqP0Pd1sg36xSZnNqLWDZuSkrVcsL11kWK/JNjGsjjjYvcjZe+7ljvvOcdfeAWf3j7h4cAgy8xKEzIXVyNN2lyyj59j2DtecOs3LXHecG7tGzhcM8y0O1yva0T5xdEAcHVADxmZWY2NvvWY/g0sWq3GCaaK1xqLrKVFIgnlfMSZbI21AlBIsSvDoU9vcdPIYGzvH2Cqim29RC2wv5k98mU/64kdzBeIBPuD1XuUzFfqcrgTzqMyr6CKIEAKajdNMmQyIlUWWnm4+Z2Oxwc68ciLEcUY2cqDzRMmGSMImJByVhsgoCGGBVWizTQ5f7k353T/9E/7093+Pi/uXcATHNhZ82vu+K6/+Si9PP58TATlN5LBkefEC0+qIcVgzDCOKoJZKKChRIZOc1qwPD1ktD1kulxzs73P2/AXuuO8Cd+0dsHu04nC9pgsxLzCLYGiNu49GnnZpxVg6draPcezESV78hms5PVxgVXvoZvS5pt+/yEaIiEKbRo7WA8tmDsaJi03sJgxTo03JlKaQyKY5OL0xJ9vEOCWLvnB+NUAEx+czHnZ8m+uObXLN5pxZ37Ez79na2KLO+s96xU//is/lCsQDvN/rvuqDulqe3pdQVwo1gq5WughqEYGRE7fGOpO1xaSA0lFnMzb6yk4JThTYkFnQmNMIG2RKFDI6LJE2Qrj2UArjzS/G35Zj/NKP/gAX9vY5XC4pi022a+HD3/YNed3XeFW2jh2nRCCJnEba8oDpcJ9pWNPaxLheM63XjOs1bRxYr44YV0uG5ZK9vT0u7B1w/mDJhcMVu0cr9tcTy2FgJticBbMSCHMwNG47WHPbpRWtdmxvn2Dj2AluvP4mTsTIqa0Z28XMLt5N3b9AtonDobGekrPrxl4zl9YTBw1WmdgwpjFiVuC6E8c4XK7Z6StH64FSK5MKfRFHw8BI4fjWFicXPY85NuPBM9je2GA23zS1e8jrfcV3PIMrEM/lQ9/4NX8h0JuqQFUlaqUvQS2FKgg3yEbLZCJAokhEBLVU5lUsSmVeYBFiHtBHECGyVFrtyQTcABGl0jZPsXyxV+PnfvyHePqtt3HxaJ+mwuapa5gPS97ndV6e137NV+Xk6dN0XU+UioEcB6blAbk+IseRNg6M64H18ojV4QGro0OO9ve5tLfLxUt7nL10xKXDgf31mtUwcjCMYHNy0bHoAgFja+ytRp6+N3L7wQp3c06cPM188xhbJ87woGtOcSIvcqYdcWrvbvpMXOesE5bjyPl1Y7/07C3XHK5HlmmWw5pJBTDhZF4qUyaLvieHgSiVPoLTHZxfD5xzB6Ww1QW3bM254dg2xzfmzLe2f/E9vurb3oxnQzyXD37j13ijQL9cIwiJiGBWC10EBRMkTjM6SQVC9CEiRFXQFdFHoYaYFTErhYiCSiFLIUtHKCAnkKhdTz7opfiH3SW/+Us/S7O4sHuR2Nym39xhPq14x5d7BK/3Gq/CNTfeyGy+QYmCasVOcljBNJDDADkxrZcMR4es9i5xtL/P4d5Fdnd3OXdxl4sHh1w6XLO/nNhbDRwMExt94fiiI5zUWliOIxeP1jxld+CeZYPac+zUGfrNHebHT/Pij34MswvP4MzRvVyzugDTRFpkmikbhw0uZXBpnLi0HDhIs06TLcnW6Gqldj2KoK+Fab1mXgrzgMzG+XXjYgYp6GtlZ2uTrlYCs7m5+cbf9RM/8ys8G+L5+Og3ea2/lfwSlaAvYlaCKlMkwokNo01GQRJVgUJEBEWiAiVESHS1EqVA7UgBCiKCThAR5OIY5cVfgx/68R/l3nvvo9aOC3u79DsnUe3ol7u8xUs8mDd4jVfn+gc9iM3tLQJBFKJWWptQm5CTkPA00oYl0+EB6/1LLC9dYH/3HBcvXuTC7h7ndg84t7/k3v0lR2Nja96xPStsdJWxNQ7XA2cPB55wccWFUUTXc+z0dcyOnWLj5Gnmiw1e4UHXsXnnP7C93GU6OmRaLfE0MqZZR+X8euJgnNhbTwyGnCZynGiIKIXaddhGmUQRUDiMwKUnSuA0LoV+NmNrY0FXAk/j333fT//8S/KcEM/Hp77Za79zBD9UgCrTCapMlSgCGRqQFkhECVBABEgUjAQioARRKkQFBSIpIWopRDcnb3oMe9vX8CM/8D2oW+A2snt4SH/8FNkmur2zvOlLPYzXeMVX4MEPezhbO8eoNQBQ7UFBjgNSUkqhRBDZaMslw/4l1vsXOLq0y6UL5zl//iz3nL3AXRf3uevSIZPFrMDJzRmzGgxTcmm55q69Ix6/O7CuG7ibcfLam4mNbY6dPsOZa69nQ8nDpwts7t7B+nCf8eiAYbVmbI116bg0TByt1qyGgWkYyJZMhiGhdh2SmJPMA2Y1qKUy9nOYzem6GdmSp5+/SKuVY8ePs7mxCTm9y/f9+E/9MM8J8XwY9MVv9waPw350kFRMkQibkBHgNFIQMiGQhBUYAAFgCSuopVJLIUK0MiM3T6BT1+NT17N588P5iz/+fX7/N3+dbjZnGieOxon+2AmGoz3mh+d4jUfdwqu/wsvzsEc+iuMnTzHre5wNRSFqARU8jRDQlUqQtNWaXB6wPtzncPc8e+fPcfH8ee49f5Hbz57n7P6S5Zhs9MGp7Q1mxSyHibMHS267eMhTDoM4dop+Y5uda27k0jDxki/5UhwNI/O+58HbHcfOP4P1wUVW+/vk6ojhcJ+LhwcslyvIRpsmxmZWCSNiUlC7jh7YypF5wKwGNURfCrO+MpstyOi5L3qm2QZZKsATvu0Hf+ixAvOcEC/A177rm70tzp/ABkxgBJAGjGyEKGE6QQAIzBUCUkKIiA5mG+jMzbRbXox26kba1nHqfJOeiV//4e/kqY//B1bjyNggoxDzBdPuvZzqGi9x4zW88ku/BI94zGM5cfI0i8WCEoCNakdEQQEgioGc8DSQqyXD4T4Huxe4dO4sl3Z3OXfpEned2+XOC3usp4kTGzNObM0Bc7Bcc9/+EU+/cMjtucXxG25h6/gpts9cz21nz3Pymms5vrPD9rEdVgf7vNTpTdZ3PImDi2cZ9i/Rjg5Z710kV0e0hLVhSLHuevYPlhxME6V2HO8r3bCikPRF9KWwPevpu47NjQ1qG1mcuZ6jxQkO+jnrcfl2X/ct3/6TPC/EC/E97/c2f2j0KkIIg42dOBMBAoKkAAWwjBEGBFhBmx+D6x8ONz+aPHMzy27BJDOfLZjVQjfs80Nf9+Xcc9edDDaLxTZH64FShXbv4drNnhtPHePlH/NIHvHox3D6mmvZ2toiBBiin9F1BSsAKBKRiYc14/KA8WCfvYvnONrb4/BoyV333stT77qHs3tHlBCntuZszTqaYe9oxd2XDnjKuQPu6U5y5uYH86CHP4rFsVMMCc+47xwbO8fJNvCyL/5ijLvnKHc/jbNP/hsW4xGzbHhcMa5XDNFzZDhYDhzaeD1wcblmZXPt5pxtzIn5jGFc05fCsXlHX4KNvmPe9WyfPsN44gbG46f/6OM/8zNelecP8UL86Ee86yvW2v2JEAJoDVqCEzwRQNhgkIKUGKNnNd9mOn4947UPYTpzI97aIRETRurou0pryaKvzJaX+N6v/CLuu+8e+sU2fdexXA/EdMTpWLJRK8e3N3ipRz6cRzzi4Zy65jp2jh1jNp/jZpDpZguiCNuUNJ4GclyTyyXrg32ODi6xt7vLxd0L3HnfWe647wJ7yzWzLrjx5DG2NuZcOjjivr0D7r50xJMuDpzvT3DDQx/BTQ97FKeuuZaNjQXzxYLV2LjjznvIWjh54jib05In/cFvM126yOkeZj1kGxnWI4f7exwdHrJer1mnORgntuY9m7OeucRyPbAa1ty8s8m1GzO2uspmDTYXcxanrqc7cZrNna1XeptP/4I/5flD/At+6bM+8huK4kOxYRxwa9AayobccMJEx3rzJNPpm1gfu4bx2DUM802G6Fi3ibTZ2txEAesJtjbn7O0fcd/FXV7quh2+/yu+gPvuu5d+vk3te9q4Jnfv5mEnN3CazY0NHvmgG3jEwx/OmWuu4/jJE8wXm0AQEaCGIiilIwCPK7xeMx0dsDo8YHm4x6ULF7hw/jx3njvHfRf3WY0jZ04c45pjmwCc393nrt197rh4wF3lJJx5ENc86CFsnjiNu57FYs7RauT2+87y5q/+Svz13/4dD374w7l2a8F9T30iv/frv8ZsvsGGJjg8z7R/gTIOtDYxpVlNjQYUwdZiQR9wuB5ZyJxe9JzoK73M5mzGsZ1tOH4tixOnv/F9vvgrPowXDPEv+MOv/OyTLdvfZms3MqyhNZxmEAwxZ9w6zXjyJg63TrOab7KySEMKpjSlVpBYzGdEBIdD4+T2BiWCIRvXz8QPfOUX8YynPYXoFtTZnLY6ZH54loed2WGcksVizi3Xn+HBN9/MddfdwPFTZ9jY3iQUSCKqECJUiBKEk7Za0pZHrA4PONq/xN75c5w7d5bb7rmXveXArO+57tQxjm9vcbQ84vZ7z3L7+T1uu3DAxa0buPYlXhE2tum3jnHhcE3tOx71oJvpSqBpzbGdHfq+59677+RlH3wjP/0jP8zt53aJqGwWE3tn4eA80zSwTmiABVViQ6Y4yUwWwM6s59g82Jkv2Jz1LIrot4/fWU+deMn3/6rvuMALhngR/N5Xf/abp/VzU4q15gzzHZZbJ1gvjrPutxgiWDUjCQOr1mgEtVaak650LFujtcZ8tmBzFtxxz33sHh3xui/5aB73az/Db/3iL1LnG9RauXDP7exo4CVuPkNOE7P5jGtPnuCG667lmuuu49Q117G9fYxaRClBRCFKB5haA1oj12um9ZLhcJ+DSxe5dP489953L+d2LzFOybGdba45eZxag4u7uzz+tju4/fwB9x6sONed4GXe5J3ZOnmSi0cDyym57/w5Xv4lHsOpzTmlVi7ddw8bFco4cduTn8iTnvxkxqgkYt7PqMDMA8vd+9jf38U20NCUbHiCTMJmJtgo4tissLPY5MSiY2ves7XYeIv3/YGf+3leOMSL6Ce+5/u/Yb04+aGrOmeoM47SNAMSXddzuFozNlNqYIlhmljM5jTg7gu7qPZce2ybe85f5NqT2yy2j/H7f/m3vN7LPIbT64t825d/EbVbMK6W3HHbk1gU84qPfDCbAbO+4/j2NtecPs2Za6/lzDXXsbOzw6zvKF1FCEWl1IIEnka8WjKsjhgO9jnc3+Pg0i4XL+2yt3+AEMePH2NnZ5txWHHbXXfzD7feyYWjgUvrkacPPa/5rh/K9dffwL2X9jlz8jgHh4es1ksec9O1rO55Bn/7l3/BHbfdwcXdXWqdE7UyZmOcJk6eOsMwjJw+eYqj/Uss+orHiXFYsn/hXvrhgBmm2PSCjRqcnHccm884Pitszuff+CE/+Rsfxr8M8SL6ht/6h61pb/fPW7ZHGRiaadk4XK05Wg1sLhY0J1Kw6AvNomWye7hkc3OT5TixOass+hmH6xXHT5xkHEeu2Vpw/VbPz37nN3P705/BhbN3cvbsXYTEi99yIw+75jiLvrA9X3DixAlOnTnDqVOnOXHyFDtbm3S10mSCikoA4HGAYUVbr1ke7nO0v8fh3kX2Lu2yPFoyWyzYOXGCWd9z8dx9PP7pz+Bp91xgjXjauT1uWwXv8LGfy4ljO5w/WrEz75jlSLe8wO/+0i/yjFtvpU0TtVaW64mt7R3GltTa4VIosznNwWKxQd9VFn1HDgOkqF1hvHQfh/fdThuOqBKLGhzrCidmHdds9E+8/tTmy3/Yj/32Af8yxL/C5/3Arz7i4uHBn85LHD8YTQloFveeO8fNN93EPefPM18smAfU+RYXd89z+/l9XvpRD2WcJnY2Fqg1ou+J2YydxYyNMBu18g+/+Yv84a//Gnff9XTWw4qQOL6x4BUe+RBObsw4vrlgc3OTE8ePc+rkKU6dOcPx48eYzxdYXCYHkshxTa6XTKslq6MDjvb3WB/ucbi/jyU2d46zubXFsDrk9tvv5O+e+nTOHg489dwet+0esnTlAz//67jp2tOspsZsWvHUP/9dfvlnfppaZgwJAsZpTTebU0plmJI6X1AXO5T5nCgdUybbO8eZdR20iRiWRBTGYSLHJRfvfhpjmp1rbqK4cen2J+3W1aVX/JOn3fFkXjSIf6XP+/5fefvb7r77x2rXs1ovIQqzvqfrOpbrga4rdBF08xkRhWEaUelYDyO3nz3PRHB2DQ9/yINZMPGIG6/h+o3Kk37nl/n1n/oJ7r3vDiQBEFG45ZrTvPjN13N8o2dnY8GJrQWnzpzh2utu4NSZa1gsFggjgR1ISQ4Dbb1iXK4Zji6xPDpgWB4yjhPdYpONzS1KCXbP3stfPe6J/M1t9/D3d1/gwmqkZaPZfOgXfxs3XnOahdf8wc/9GL/1m7/Baj2ys32CyZBRqP2McZqIqNBVkJgINraPU7o5XanMNjaJrrJcrfE0sFGC2kb2j5acPHMt67HRnzjJ9vYxNjS9w7d/0cf/OC86xL/Bh3zrL3xK7bovFKafzykBpVRuu/ccR6sVs1qYz3pm8wVtGllsbTHre84fLJnWS+7eP+J1X/bFecatz+Dm667l5s3K3/zyz/CrP/0j7F66gCK4X60dN19zhsfcdA0bBU4f2+L6a67h5ptv4Zrrrmd7e4dCYicYnMk0rvE4Mhwdsj64xHq1YhoHuvmcfrHBbDZnebDPn/z1X/Obf/MEnnTfJQ6mJC0EjIbP/bYf4bpF4Rd/5Pv58z/8fXYPDmgkO5vHaNGRBkv08wWJmDKZANeerZ0TzBebqCVlNuf4ydNcOjyihBlWa2omOa6opaDasbm5jSqf+tPf8sVfxL8O4t/oHb74B7661PJR115zmmNbmxyt1txx9jwJbG1ucmp7k9IVTm1tMIyN+y4dct3p45y/eIGdrU0eeuN1/MRv/gGv/FIvznV5xO/+yHfz27/5ywzThHg2RVAiuOn0KR7zoJvY7AontjZ41MMewkMf9nCOHz9OiYRpoo0Tbo0cR3JcM6yWDMtDpmGk9IX55jZlNufgaMUv/dbv8Kt/+Q+cPVwzJdjGAglamfOl3/4D/O2v/zy/+Yu/xHw+456z95ISW5s7ROlZTROqHbXrqbM5GQVqT0ZhsbXDxnyDcbVkMmyfOEmTKBHMZnPW6xUeJ4ajI9T19F39ml/5ri/5aP71EP8O7/l1P/XdN11/zXttLmacvbDHpcMl53b3WGxvc8uZ4yjEsY0F49hQ7TixNWd1dMRjH3w9h+uJ7/3pX+DtXvfVuftPfoff+fmf4IlPfxIQPIuEgJCIKGxvzHnQ9ddzcnPBzdee5hVe+qW56cbrmQcMRwdM44CnhtvItF4yDgNgQqLOF4yl8sd/8w/8yh/8Kbdf2GcggMQWAgyIZCxzPvlzv4gf/NqvICdTJe7bPQdR2FhsUrsZkyEjiNJBqbTSURebUAo7J04RKgyrFUVCXQ9dz2LWMyFm/YyuVmjJuF5+zy986+e/N/82iH+H1/7s36qv9ZLz79tczN753O4+5y7ts3u4ZnN7gzM723RdZaPvqKWwmHXgZGgT+0dHLIeJl7rxFPtP/Qd+/vu/j/2L93HbfXcTCgBsQEaIQBBCCkJiVivXnNjhUQ99KC/3ki/O9TsbTPu7LIeBaWq0ccBtJNNMTi4eLrn13nP8zZOfzrn9Q1IVA3ZiAIEQaRCJNk7wHh/ykfzy9303lUBMnL1wDnUd835O38+ZENQOlYpLRyNgNqMuNlhsbCOD08hJSxN9x8bWDhOwtblNVwubi/kP317Ov8dvf/ZnT/zbIP6dPvu3fqtuLo99+/n9/fe658Il9lcji8WCEzvbzLpgczaj6yontjY4OlqybiM1xMZ8xiO2gl/9nm/nSU98Evfceyf3XTyHJIRAAhsAyeAgShASCDCExGI25+TWgs2+UqIQUZC4bJomLuxd4uLBklVrJCALEMYYIwkAYyAIAdun+OTP+zJ+/Nu+mXN33sFiFtx37izRzdiYL6BUonS4VMp8gboZDTEqUDdn+9hxaI1hNVBqoUgMw8Bi5ziOws7ODhLfs398/f6//dmfPfFvh/gP8qk/+jtffff5vY+672DJxsaC60+eQCQntrbou8KJ7Q32Dw4pMo++6VqW65H7nvZ4fvdHv597776b+87ezd7hISGukIgAp7lCAEhCEpIAEVxhGdIgEQoEtGzYYIwNxgghwAIJ7AQLRSGi4GyMZcaXf8t38UNf/zU8/WlPp4TZO9inzBbM+hm19qRNlopmC7qNbRyFkcBR2dw5RlHgaaLZ9CHW64HZxgZRCouNxdf80jd+9kfz74f4D/QB3/4rn7K3XH3hse1Nrj2+zdSSY5sbnNqeg4I7zu6yPas8+sYzXDxacsetT+dpv/lzPOnv/45z5+5if7kCgRCSkESEMJAtuZ8kxDNJBMLiCgOCQGQ2bEiMJO4nifsZEwoApEKbJoYUX/kd38v3fennc7AcyUzuuXCemC2YLzaotWMaRxyVFoX58ZO00pOl4CgsNrboopDrFaqVra0tVqsVtGRW66f+6nd98RfxHwPxH+z9v+1X3p5Svu3Mse3jXRXHthYc35izWo885a5z7Cw6jm1v8CePfyoPOz7j7t/+WZ7+hCdy7vw9XFoeEQgASUhCIQCEsI0NYAAkIQswFggAISAxkNhCEkJIQToBAyAJABChQpLkNLJxzc183dd9A9/6xZ/DLdec5m8e91SefvYcdXObvp/T1cqUyWRw11E3j6HZBlOafmOT+XyDjmQ83MelcuLMGcYpdwv+gF/6xs/+cf7jIP4TvPd3/eojTmxs/NzmvH/UsY05x7cWXDo44vG33s3O1ga7BwesEK90quO3vueb2LtwkXPn7mb38JAQgJCEJCQhCakgCQBs0g2nkbhMCGNAgAEwIACDBVIgCSmwG7axk4gKgtaSzMZLvs6b85kf9zF81ed+Jvc94+lkmXPH7kW6zWP0szkRBZVKA8YEzTaIzW2in9EiOHH8BLm3S66OqJs7bBw/9sQCb/HzX/sZT+Y/FuI/yWf/6G9tsXn8SzZn9UO3Zj33XbjEnz/hadx803XccuoY1506Rn/uGXzf13wZbuLuu57Bxf09QoEAhTBQFFggFUICjBQYEGAndoIhDcYIAEGAAEkgcBopAJE5YRspiAgApmkkCd7pQz+O93yrN+eHvuM7+IPf/z0W8w2edtcd1O2TzDe2ESa6GQ1IRKs92twmuhl1scmiq8T+RY4uXaTfOfGN9cTJT/rtb/zsA/7jIf6TfdMfPunNsb/5aXfcd+Pv/NXjeakXeziPvOYEewf7PHgDfunbv4EL5y6wf+kc91w4R1EAAoEkQoIQQSEUGIMEAgwCwNhGCpAwBoMASNLGNiCkwJhsE5KQChFBZmMaR6J2vMqbvjUf8G7vzE98x3fwN3/3OLr5nDvvu4967BQbW8ewTS09y2mk39om64wxKv3mFnW2YLME49k779y/cPGD//I3fuTn+c+D+C/wlX/4Dyef9Pg7Pu/X/+bxH/pyL/YoXvrB1/OkW2/n9FZPPPVv+Mvf/A0O9i9wx7l7CURICGGBJBQiCCICFDw/thH3Ewhsg5N0IoSiANDaBBhFIRREBNM0Mk0TpVRueuxL8R7v8Lb8zA/8IGcv7nNs5xjPuO8e6vYpNrePsV4t6boZQ2toY4t+c4e1BfM5W1vbbNb4Rt197jN+5ce+6gL/uRD/ha774C95xcc+9KFf/Tov8YhXGZeHdPMZp9sRf/0LP84f/v5vcWnvEpIIBSFhQCEApIJkQgVjQABIAkCCTAMgCduQiZ04glAQEbQ2kdmIEFCQBIJpHMlMutpx8iGP5t3f8k345V/4VWalYz2OPOPsvZRjp9ncOsa4XhK1Z0KMpTLfOYlmc47Sf3R8Z+ujf+/rPv1P+a+B+G/w0T/2+2/70FPHvuDg8PDRN5w5wV1/+fv89Hd/G3ffexdFgQySUAiioDQqhftJAkASADJYPIud2MkVQYQAkZlkNiSQCgBRCmQyjCtM0Hc91z725XivN3kdvvGbvpVZP+PEyWu489w5vHmMja3jtDahUrGCqRRG6hP6nWOf9pff96U/yX8txH8T23q3r/3xd3r7133VT336X//RS/zcd38rT33S44kSFAVYqAgQRQVjJAFCIcQDGCwusxNszBVSIAljsjWMkQIBUhARtDYxjWsUHaXrecU3eztebCP44Z/5BeaLLc5ccy13nj2Ltk7QzTaYWqPUDmr5u8n6wr/62W//EZD5r4f4H+BHfvNP3ugHv/7LP/Iv/+yP3yRKKCRARAQgpAAgIgAQVygC0hhAAMbmOUgCwDatTUgChCQiAkmM45rWGrX2ODre6cM/js0L9/ITv/jrbG0sOHnyJM+46y7YOk6dLyzVXypRv/aPfubbfoX/Xoj/QR7ykIc8qLm9V1F5V0mPAlCIUAGEJAAk8UC2iRA2ZCYAEYFtJAGQOWEbCCQBopTATtbDGgx917GOno//wq/khgI/9EM/xtl77uL4yZM84847nujNnR8MbX7PX/3mDz6D/xkQ/0M9/OEPf9nW/DYRerNQeRkEkpAEgG0kAWAbSdhGAhskcYXJTOzEFhJEBFIgidYmxnGNVJj1M9bdgs/6mm/lmnbIt3/jt/zV7t7RL2xszH7q53/+R/6S/3kQ/ws8+MGPva7vp9e29FqBXhH04kDPczA2GCNERABgJ61NAICQhBSUUrDNOI20aSRKGfp+8feeb//pJ3zel//OSz7k+G+/4ou92D38z4b4X+jhD3/4TOofA/kYiUdYPFjmJuAaiVOStkEbtmvmRGZOwJEU+xFxntB9Neod0zTdOk3tyZnj42utj3/KU56y5n8X/hFu4PgbjsuodAAAAABJRU5ErkJggg==",
						alt: "avatar"
					})
				})
			}),
			l && /* @__PURE__ */ m("div", {
				className: "qrcode-icon-layer",
				children: /* @__PURE__ */ m("div", {
					className: "qrcode-icon-placeholder",
					children: /* @__PURE__ */ m("img", {
						src: r || "data:image/png;base64,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",
						alt: "app icon"
					})
				})
			}),
			u && /* @__PURE__ */ h("div", {
				className: "qrcode-error-layer",
				children: [/* @__PURE__ */ m("button", {
					type: "button",
					className: "qrcode-refresh-icon",
					onClick: a,
					"aria-label": "Refresh QR code",
					children: /* @__PURE__ */ m(Fm, {})
				}), /* @__PURE__ */ m("p", {
					className: "qrcode-error-text",
					children: i
				})]
			}),
			d && /* @__PURE__ */ m("div", {
				className: "qrcode-loading-layer",
				children: /* @__PURE__ */ m(Im, {})
			})
		]
	});
}
function Pm() {
	return /* @__PURE__ */ h("svg", {
		"aria-label": "QR Code",
		className: "qrcode-svg",
		role: "img",
		shapeRendering: "crispEdges",
		viewBox: "0 0 21 21",
		xmlns: "http://www.w3.org/2000/svg",
		children: [/* @__PURE__ */ m("rect", {
			className: "qrcode-svg__background",
			height: "21",
			width: "21"
		}), /* @__PURE__ */ m("path", {
			className: "qrcode-svg__modules",
			d: Mm
		})]
	});
}
function Fm() {
	return /* @__PURE__ */ m(Z, {
		name: "arrow_clockwise",
		size: 24
	});
}
function Im() {
	return /* @__PURE__ */ m("svg", {
		width: 40,
		height: 40,
		viewBox: "0 0 40 40",
		fill: "none",
		"aria-hidden": "true",
		children: /* @__PURE__ */ m("circle", {
			cx: "20",
			cy: "20",
			r: 14.6,
			stroke: "currentColor",
			strokeWidth: 2.17
		})
	});
}
//#endregion
//#region src/components/Views/QRCode/index.ts
var Lm = /* @__PURE__ */ _({
	QRCode: () => Nm,
	qrCodeStates: () => jm,
	qrCodeTypes: () => Am
}), Rm = [
	"2line",
	"title",
	"text",
	"Spinner"
], zm = [
	"arrow up",
	"icon",
	"text",
	"arrow"
], Bm = ["Enabled", "Disabled"];
function Vm() {
	return /* @__PURE__ */ m(Z, {
		className: "subheader__arrow-icon",
		name: "chevron_right",
		size: 24,
		style: {
			fontSize: 18,
			width: 12
		}
	});
}
function Hm() {
	return /* @__PURE__ */ m(Z, {
		className: "subheader__arrow-icon",
		name: "chevron_up",
		size: 24
	});
}
function Um({ 左侧类型: e = "2line", 右侧类型: t = "text", right: n = !0, 状态: r = "Enabled", 标题: i = "Content subheading", 副标题: a = "subheading", 左侧文本: o = "subheading", 操作文本: s = "more", select选项: c = [{
	value: "1",
	label: "Option 1"
}, {
	value: "2",
	label: "Option 2"
}], select值: l, onSelectChange: u, onAction: d, className: f, children: g, ..._ }) {
	let v = r === "Disabled", y = n;
	return /* @__PURE__ */ h("div", {
		className: X("subheader", `subheader--left-${e}`, `subheader--right-${t.replace(/\s+/g, "-")}`, `subheader--state-${r}`, n ? "subheader--right-on" : "subheader--right-off", f),
		"aria-disabled": v || void 0,
		"data-left-type": e,
		"data-right-type": t,
		"data-right": n,
		"data-state": r,
		..._,
		children: [
			/* @__PURE__ */ h("div", {
				className: "subheader__left",
				children: [
					e === "2line" && /* @__PURE__ */ h(p, { children: [/* @__PURE__ */ m("span", {
						className: "subheader__title",
						children: i
					}), a && /* @__PURE__ */ m("span", {
						className: "subheader__subtitle",
						children: a
					})] }),
					e === "title" && /* @__PURE__ */ m("span", {
						className: "subheader__title",
						children: i
					}),
					e === "text" && /* @__PURE__ */ m("span", {
						className: "subheader__subtitle-text",
						children: o
					}),
					e === "Spinner" && /* @__PURE__ */ m(da, {
						尺寸: "Medium",
						状态: v ? "Disabled" : "Enabled",
						options: c,
						value: l,
						defaultValue: l,
						onValueChange: u,
						placeholder: "Select"
					})
				]
			}),
			y && /* @__PURE__ */ h("div", {
				className: "subheader__right",
				children: [
					t === "text" && /* @__PURE__ */ m("button", {
						type: "button",
						className: "subheader__action subheader__action--emphasize",
						disabled: v,
						onClick: d,
						children: s
					}),
					t === "arrow" && /* @__PURE__ */ h("button", {
						type: "button",
						className: "subheader__action subheader__action--secondary",
						disabled: v,
						onClick: d,
						children: [/* @__PURE__ */ m("span", {
							className: "subheader__action-text",
							children: s
						}), /* @__PURE__ */ m(Vm, {})]
					}),
					t === "arrow up" && /* @__PURE__ */ m("button", {
						type: "button",
						className: "subheader__action subheader__action--secondary",
						disabled: v,
						onClick: d,
						children: /* @__PURE__ */ m(Hm, {})
					}),
					t === "icon" && /* @__PURE__ */ h("div", {
						className: "subheader__icon-group",
						"aria-hidden": "true",
						children: [
							/* @__PURE__ */ m(Z, {
								name: "share",
								size: 24,
								className: "subheader__share-icon"
							}),
							/* @__PURE__ */ m(Z, {
								name: "share",
								size: 24,
								className: "subheader__share-icon"
							}),
							/* @__PURE__ */ m(Z, {
								name: "share",
								size: 24,
								className: "subheader__share-icon"
							})
						]
					})
				]
			}),
			g
		]
	});
}
//#endregion
//#region src/components/Views/SubHeader/index.ts
var Wm = /* @__PURE__ */ _({
	SubHeader: () => Um,
	subheaderLeftTypes: () => Rm,
	subheaderRightTypes: () => zm,
	subheaderStates: () => Bm
});
//#endregion
//#region src/components/Views/TextClock/TextClock.tsx
function Gm({ 类型: e = "Number", 时间: t = "17:00", 日期: n = "Monday, March 13th, 2023", className: r, ...i }) {
	let a = e === "Number", o = e === "Center with simplify date";
	return /* @__PURE__ */ h("div", {
		className: X("hm-text-clock", a && "hm-text-clock--number", o && "hm-text-clock--center-simplify", !a && !o && "hm-text-clock--center", r),
		...i,
		children: [a && /* @__PURE__ */ m("p", {
			className: "hm-text-clock__time",
			children: t
		}), /* @__PURE__ */ m("p", {
			className: "hm-text-clock__date",
			children: n
		})]
	});
}
//#endregion
//#region src/components/Views/TextClock/text-clock.constants.ts
var Km = [
	"Number",
	"Center with simplify date",
	"Center"
], qm = /* @__PURE__ */ _({
	TextClock: () => Gm,
	textClockTypes: () => Km
}), Jm = ["Phone"];
function Ym({ 内容: e = "Toast content", 类型: t = "Phone", 底部偏移: n, className: r, style: i, ...a }) {
	let o = /* @__PURE__ */ m("div", {
		className: X("hm-toast", "inline-flex items-center justify-center gap-2.5", "min-h-9 rounded-[18px] px-4 py-2", "backdrop-blur-[40px]", "shadow-[0_10px_60px_rgba(0,0,0,0.2)]", "font-['HarmonyHeiTi',var(--font-sans)] text-[14px] font-normal leading-[19px] tracking-normal", "text-[var(--harmony-font-primary)]", "whitespace-nowrap select-none", r),
		style: {
			backgroundColor: "var(--COMPONENT_ULTRA_THICK_fill)",
			...i
		},
		role: "status",
		"aria-live": "polite",
		...a,
		children: e
	});
	return n === void 0 ? o : /* @__PURE__ */ m("div", {
		className: "absolute left-0 right-0 flex justify-center",
		style: {
			bottom: `${n}px`,
			zIndex: 60
		},
		children: o
	});
}
//#endregion
//#region babel-demo/all-components.generated.ts
var Xm = {
	"Container/Card": ut,
	"Container/DialogPhone": St,
	"Container/FloatingBindSheet": Ft,
	"Container/FloatingDialog": tn,
	"Container/ListPhone": nr,
	"Container/Popup": or,
	"Controls/ActionBar": _r,
	"Controls/Button": mn,
	"Controls/Chips": Sr,
	"Controls/FloatingActionBar": Cr,
	"Controls/FloatingButtonPhone": Fr,
	"Controls/FloatingChips": zr,
	"Controls/FloatingMenu": $r,
	"Controls/FloatingSelectPhone": Di,
	"Controls/FloatingTextSelection": Ni,
	"Controls/FloatingToolBarOnlyiconPhone": Gi,
	"Controls/FloatingToolBarTextPhone": ra,
	"Controls/Menu": gi,
	"Controls/ScrollBar": oa,
	"Controls/Select": ya,
	"Controls/TextSelection": Ea,
	"Controls/TextSelectionHandle": ja,
	"Controls/Toggle": Fa,
	"Controls/ToolBar": Ka,
	HMSymbolIcon: at,
	Icon: ro,
	"Input/Counter": ho,
	"Input/FloatingSearchPhone": xo,
	"Input/FloatingSearchSecondPagePhone": Do,
	"Input/PatternLock": Ro,
	"Input/Search": Xo,
	"Input/TextInput": fs,
	"Navigation/BottomTab": Is,
	"Navigation/ChipsTab": Xs,
	"Navigation/FloatingChipsTabPhone": ac,
	"Navigation/FloatingSwiperDotPhone": Sc,
	"Navigation/FloatingTab": Pc,
	"Navigation/FloatingTitleBar": hl,
	"Navigation/LoadingProgressBar": vl,
	"Navigation/Swiper": El,
	"Navigation/SwiperDot": Pl,
	"Navigation/TitleBar": Yl,
	"Publis/Aibottombar": Ql,
	"Publis/IconButton": no,
	"Publis/Pattern": xu,
	"Publis/Size": ju,
	"Publis/StatusBar": il,
	"Selection/CheckBox": yn,
	"Selection/CheckboxGroup": Fu,
	"Selection/FloatingPickerDialog": nd,
	"Selection/FloatingSegmentedButton": ud,
	"Selection/Picker": Ku,
	"Selection/RadioPhone": Cn,
	"Selection/RatingPhone": pd,
	"Selection/SegmentedButton": Cd,
	"Selection/Slider": Id,
	"Selection/SwitchPhone": Dn,
	"Views/AlphabetIndexer": Kd,
	"Views/AlphabetIndexerLable": Qd,
	"Views/Badge": nf,
	"Views/DataPanelLinearGradient": Df,
	"Views/DataPanelLoading": Af,
	"Views/DataPanelProgressCircle": zf,
	"Views/Divider": zt,
	"Views/FloatingAlphabetIndexerLable": qf,
	"Views/FloatingPopupTip": op,
	"Views/FloatingSnackbar": Ep,
	"Views/FloatingToast": kp,
	"Views/GaugeRing": $p,
	"Views/GaugeStripGauge": mm,
	"Views/PopupTip": uu,
	"Views/ProgressBar": _m,
	"Views/ProgressBarCapsule": bm,
	"Views/ProgressBarEclipse": wm,
	"Views/ProgressBarLoading": km,
	"Views/QRCode": Lm,
	"Views/Snackbar": gp,
	"Views/SubHeader": Wm,
	"Views/TextClock": qm,
	"Views/Toast": /* @__PURE__ */ _({
		Toast: () => Ym,
		toastTypes: () => Jm
	})
};
//#endregion
//#region src/container-components/ListContainer/list-container.tsx
function Zm({ as: e, children: t, className: n, "data-slot": r = "list-container", ...i }) {
	return /* @__PURE__ */ m(e ?? "div", {
		className: X(n),
		"data-slot": r,
		...i,
		children: t
	});
}
//#endregion
//#region src/container-components/GridContainer/grid-container.tsx
function Qm({ as: e, children: t, className: n, "data-slot": r = "grid-container", ...i }) {
	return /* @__PURE__ */ m(e ?? "div", {
		className: X(n),
		"data-slot": r,
		...i,
		children: t
	});
}
//#endregion
//#region src/container-components/NavigationContainer/navigation-container.tsx
function $m({ as: e, children: t, className: n, "data-slot": r = "navigation-container", ...i }) {
	return /* @__PURE__ */ m(e ?? "div", {
		className: X(n),
		"data-slot": r,
		...i,
		children: t
	});
}
//#endregion
//#region src/container-components/index.ts
var eh = /* @__PURE__ */ _({
	GridContainer: () => Qm,
	ListContainer: () => Zm,
	NavigationContainer: () => $m
});
//#endregion
//#region babel-demo/design-components-entry.tsx
window.DesignComponents = {
	React: t,
	ReactDOMClient: f,
	...eh,
	ComponentModules: Xm,
	ContainerComponents: eh,
	cn: X
};
//#endregion
export { pr as ActionBar, Zl as Aibottombar, Ud as AlphabetIndexer, Zd as AlphabetIndexerLable, ef as Badge, Fs as BottomTab, sn as Button, lt as Card, Yc as CellSignalIcon, vn as CheckBox, Pu as CheckboxGroup, xr as Chips, Ks as ChipsTab, Ys as ChipsTabPhone, Xm as ComponentModules, eh as ContainerComponents, mo as Counter, kt as DEFAULT_SHEET_SNAP_HEIGHTS, Tf as DataPanelLinearGradient, kf as DataPanelLoading, Rf as DataPanelProgressCircle, xt as DialogPhone, bt as DialogPhonePanel, $ as Divider, Zc as DualCardIcon, mr as FloatingActionBar, Gf as FloatingAlphabetIndexerLable, Mt as FloatingBindSheet, Mr as FloatingButtonPhone, Rr as FloatingChips, ic as FloatingChipsTabPhone, Jt as FloatingDialog, Yt as FloatingDialogButtonGroup, Yr as FloatingMenu, ed as FloatingPickerDialog, ap as FloatingPopupTip, ip as FloatingPopupTipArrow, bo as FloatingSearchPhone, So as FloatingSearchSecondPagePhone, sd as FloatingSegmentedButton, yi as FloatingSelectPhone, Tp as FloatingSnackbar, xc as FloatingSwiperDotPhone, Nc as FloatingTab, Mi as FloatingTextSelection, ml as FloatingTitleBar, Op as FloatingToast, Wi as FloatingToolBarOnlyiconPhone, na as FloatingToolBarTextPhone, Qp as GaugeRing, pm as GaugeStripGauge, Qm as GridContainer, Z as HMSymbolIcon, to as Icon, to as IconButton, Zm as ListContainer, Rn as ListPhone, _l as LoadingProgressBar, hi as Menu, $m as NavigationContainer, yu as Pattern, Lo as PatternLock, Uu as Picker, Bu as PickerColumn, Gu as PickerDialog, Lu as PickerItem, ar as Popup, ir as PopupArrowPositions, rr as PopupDirections, lu as PopupTip, cu as PopupTipArrow, hm as ProgressBar, ym as ProgressBarCapsule, Cm as ProgressBarEclipse, Dm as ProgressBarLoading, Nm as QRCode, Sn as RadioPhone, fd as RatingPhone, t as React, f as ReactDOMClient, aa as ScrollBar, ia as ScrollBarThumb, Ko as Search, qo as Search2in1, Wo as SearchIcon, Yo as SearchIconButton, yd as SegmentedButton, Sd as SegmentedButtonItemInternal, da as Select, va as Select2in1, $c as SingleCardIcon, Au as Size, ku as SizeFoldable, Du as SizePhone, Ou as SizeTablet, jd as Slider, Md as SliderSeekbar, hp as Snackbar, pp as SnackbarCloseIcon, rl as StatusBar, Um as SubHeader, Tl as Swiper, Nl as SwiperDot, En as SwitchPhone, Gm as TextClock, ds as TextInput, cs as TextInputBoxPhone, us as TextInputMutiPhone, ls as TextInputNonePhone, Ta as TextSelection, Aa as TextSelectionHandle, Jl as TitleBar, Ym as Toast, Pa as Toggle, Ga as ToolBar, Go as VoiceIcon, el as WifiIcon, lr as actionBarCounts, lr as floatingActionBarCounts, cr as actionBarPorts, cr as floatingActionBarPorts, ur as actionBarTransparencies, ur as floatingActionBarTransparencies, qd as alphabetIndexerLableTypes, Ld as alphabetIndexerTypes, $d as badgeVariants, gs as bottomTabCounts, vs as bottomTabIndicatorModes, _s as bottomTabLandOptions, ys as bottomTabLayouts, nn as buttonSizes, an as buttonStates, rn as buttonTypes, ot as card尺寸Options, nl as cellSignalTypes, Jc as cellTypes, gn as checkBoxSelecteds, _n as checkBoxStates, hn as checkBoxTypes, Mu as checkboxGroupHyperlinks, Nu as checkboxGroupStates, vr as chipsStates, Bs as chipsTabBarMaterials, zs as chipsTabBarTypes, Rs as chipsTabMaterials, Ls as chipsTabStates, X as cn, io as counterTypes, dt as dialogPhoneTypes, Cf as dpLinearGradientSizes, wf as dpLinearGradientVisualMap, Nf as dpProgressCircleRadiusMap, Lf as dpProgressCircleShadowBlurLarge, Mf as dpProgressCircleSizeMap, jf as dpProgressCircleSizes, Pf as dpProgressCircleStrokeMap, Ff as dpProgressCircleValueFontSizeMap, If as dpProgressCircleValueLineHeightMap, Xc as dualCardGOptions, Vf as floatingAlphabetIndexerLableOpacities, Bf as floatingAlphabetIndexerLableTypes, Ot as floatingBindSheetContentOptions, Dt as floatingBindSheetRightIconOptions, Et as floatingBindSheet状态Options, Tt as floatingBindSheet通透度Options, Dr as floatingButtonPhoneOpacities, wr as floatingButtonPhoneSizes, Er as floatingButtonPhoneStates, Tr as floatingButtonPhoneTypes, Zs as floatingChipsTabPhoneMaterials, Qs as floatingChipsTabPhoneTypes, Wt as floatingDialogButtonGroup个数Options, Ut as floatingDialogButtonGroup类型Options, Ht as floatingDialogMaskOptions, Gt as floatingDialogVariantWidthMap, Bt as floatingDialog类型Options, Vt as floatingDialog通透度Options, Vr as floatingMenuGroupCounts, Ur as floatingMenuItemStates, Hr as floatingMenuOpacities, td as floatingPickerDialogOpacities, Yf as floatingPopupTipTransparencies, Jf as floatingPopupTipTypes, vo as floatingSearchPhoneOpacityOptions, go as floatingSearchPhoneSearchOptions, _o as floatingSearchPhoneStateOptions, Eo as floatingSearchSecondPagePhoneOpacityOptions, ad as floatingSegmentedButtonItem状态, rd as floatingSegmentedButton组数, id as floatingSegmentedButton通透度, Ei as floatingSelectPhoneOpacities, wi as floatingSelectPhoneSizes, Ti as floatingSelectPhoneStates, yp as floatingSnackbarLeftIconTypes, _p as floatingSnackbarLeftRegions, vp as floatingSnackbarRightRegions, bp as floatingSnackbarTextButtonStates, xp as floatingSnackbarTransparencies, dc as floatingSwiperDotPhoneCounts, sc as floatingSwiperDotPhoneOpacities, lc as floatingSwiperDotPhoneSizes, cc as floatingSwiperDotPhoneStates, uc as floatingSwiperDotPhoneTypes, Ai as floatingTextSelectionLabels, Oi as floatingTextSelection语言Options, ki as floatingTextSelection通透度Options, sl as floatingTitleBarIconOptions, ol as floatingTitleBarTransparencies, al as floatingTitleBarTypes, Dp as floatingToastTransparencies, Li as floatingToolBarOnlyiconPhoneStates, Ii as floatingToolBarOnlyiconPhoneTransparencies, Fi as floatingToolBarOnlyiconPhoneVariants, Yi as floatingToolBarTextPhoneStates, Ji as floatingToolBarTextPhoneTransparencies, qi as floatingToolBarTextPhoneVariants, tm as gaugeStripGaugeSizes, em as gaugeStripGaugeTypes, ns as graySceneValues, gd as groupCountValues, Lt as hmDividerOrientations, It as hmDividerSizes, Rt as hmDividerVariants, nt as hmSymbolGlyphs, Qe as hmSymbolGlyphsGenerated, $e as hmSymbolUnicodeByName, rt as hmSymbolUnicodes, qa as iconButtonOptions, qa as iconOptions, Ya as iconButton尺寸Options, Ja as iconButton通透度Options, Ja as icon通透度Options, bl as iconSizes, hd as iconVisibilityValues, tr as isValidLeftForLines, Cu as landOptions, Nn as listPhoneLeftOptionsByLines, Mn as listPhoneLeftTypes, kn as listPhoneLine1LeftTypes, An as listPhoneLine2LeftTypes, jn as listPhoneLine3LeftTypes, On as listPhoneLines, Pn as listPhoneRightTypes, gl as loadingProgressBarSegments, ri as menuGroupCounts, ni as menuItemStates, ti as menuItemTypes, ai as menuPositions, ii as menuTransparencies, ei as menuTypes, md as multiSelectionValues, bu as patternLayoutOptions, Vu as pickerDialogPickerTypes, Vu as pickerTypes, Wu as pickerDialogStates, Iu as pickerItemTypes, $l as popupTipTypes, vd as positionValues, gm as progressBarCacheOptions, vm as progressBarCapsuleStates, Sm as progressBarEclipseIcons, Tm as progressBarLoadingSizes, xl as progressCounts, jm as qrCodeStates, Am as qrCodeTypes, bn as radioPhoneSelecteds, xn as radioPhoneStates, dd as ratingValues, rs as rightIconTypes, Uo as searchIconButtonRadiusOptions, Ho as searchIconButtonStateOptions, Bo as searchStateOptions, zo as searchToggleOptions, Vo as searchTransparencyOptions, pa as select2in1Sizes, ma as select2in1States, sa as selectSizes, ca as selectStates, Qc as singleCardGOptions, Su as sizeTypes, Ed as sliderSeekbarStates, Td as sliderStates, wd as sliderTypes, lp as snackbarLeftIconTypes, sp as snackbarLeftRegions, cp as snackbarRightRegions, up as snackbarTextButtonStates, _d as stateValues, ao as stepperTypes, Rm as subheaderLeftTypes, zm as subheaderRightTypes, Bm as subheaderStates, Ol as swiperDotCounts, Dl as swiperDotTypes, yl as swiperVariants, wn as switchPhoneSelecteds, Tn as switchPhoneStates, Km as textClockTypes, ts as textInputStates, es as textInputTypes, Da as textSelectionHandle属性Options, xa as textSelection尺寸Options, ba as textSelection语言Options, Fl as titleBarCategories, Il as titleBarIconOptions, Ll as titleBar通透度Options, Jm as toastTypes, Ma as toggleStates, Na as toggleTypes, La as toolbarCounts, Ia as toolbarLands, Ra as toolbarPortStates };
