/*global $ d3 */
"use strict";
// Avoid `console` errors in browsers that lack a console.
(function() {
    var method;
    var noop = function () {};
    var methods = [
        'assert', 'clear', 'count', 'debug', 'dir', 'dirxml', 'error',
        'exception', 'group', 'groupCollapsed', 'groupEnd', 'info', 'log',
        'markTimeline', 'profile', 'profileEnd', 'table', 'time', 'timeEnd',
        'timeStamp', 'trace', 'warn'
    ];
    var length = methods.length;
    var console = (window.console = window.console || {});

    while (length--) {
        method = methods[length];

        // Only stub undefined methods.
        if (!console[method]) {
            console[method] = noop;
        }
    }
}());

function add_commas(number, pfix) {
    var prefix = typeof(pfix) !== 'undefined' ? pfix : '',
		mod, output, i;
	if (number < 0) {
		number *= -1;
		prefix = "-" + prefix;
	}
	number = String(number);
	if (number.length > 3) {
		mod = number.length % 3;
		output = (mod > 0 ? (number.substring(0,mod)) : '');
		for (i=0 ; i < Math.floor(number.length / 3); i += 1) {
			if ((mod === 0) && (i === 0)) {
				output += number.substring(mod+ 3 * i, mod + 3 * i + 3);
			} else {
				output+= ',' + number.substring(mod + 3 * i, mod + 3 * i + 3);
			}
		}
		return (prefix+output);
	}
	return prefix+number;
}

//support Array.indexOf in pre-EMCA-262
//https://developer.mozilla.org/en/JavaScript/Reference/Global_Objects/Array/indexOf
if (!Array.prototype.indexOf) {  
    Array.prototype.indexOf = function (searchElement /*, fromIndex */ ) {  
    	if (this === null) {  
			throw new TypeError();  
		}  
		var t = Object(this);  
		var len = t.length >>> 0;  
		if (len === 0) {  
			return -1;  
		}  
		var n = 0;  
		if (arguments.length > 0) {  
			n = Number(arguments[1]);  
			if (n !== n) { // shortcut for verifying if it's NaN  
				n = 0;  
			} else if (n !== 0 && n !== Infinity && n !== -Infinity) {  
				n = (n > 0 || -1) * Math.floor(Math.abs(n));  
			}  
		}  
		if (n >= len) {  
			return -1;  
		}  
		var k = n >= 0 ? n : Math.max(len - Math.abs(n), 0);  
		for (; k < len; k += 1) {  
			if (k in t && t[k] === searchElement) {  
				return k;  
			}  
		}  
		return -1;  
	};
}

// Place any jQuery/helper plugins in here.

/* ===== Crockford helper functions ===== */
// define new methods. See examples below
Function.prototype.method = function (name, func) {
    this.prototype[name] = func;
    return this;
};

//specifies the prototype of a new object
if (typeof Object.beget !== 'function') {
    Object.beget = function (o) {
		var F = function () {};
		F.prototype = o;
		return new F();
	};
}

/* ===== Number methods ===== */
Number.method('integer', function (  ) {
    return Math[this < 0 ? 'ceiling' : 'floor'](this);
});

Number.method('toOrdinal', function() {
    var n = this % 100,
        suffix = ['th', 'st', 'nd', 'rd', 'th'],
        ord = n < 21 ? (n < 4 ? suffix[n] : suffix[0]) : (n % 10 > 4 ? suffix[0] : suffix[n % 10]);
    return this + ord;
});

/* ===== String methods ===== */
String.method('trim', function (  ) {
    return this.replace(/^\s+|\s+$/g, '');
});

String.method('deentityify', (function () {
    // The entity table. Created in a closure 
	var entity = {
		quot: '"',
		lt:   '<',
		gt:   '>'
	};
    // Return the deentityify method.
	return function () {
		return this.replace(/&([^&;]+);/g,
			function (a, b) {
				var r = entity[b];
				return typeof r === 'string' ? r : a;
			}
		);
	};
})());

/* ===== Math methods ===== */
//log-base-N
function logN (N, base) {
    base = typeof (base) !== "undefined" ? base : 10;
	return Math.log(N) / Math.log(base);
}

//random integer
function randInt(N) {
	return Math.floor(N * Math.random());
}

/* page init */
$('#embedcode').html('&lt;iframe src="' + document.URL + '" width="630" height="625" scrolling="no"&gt;&lt;/iframe&gt;');
$('#embedbox').css("display", "none");
$('#embed').bind("click", function (e) {
    $('#embedbox').css("display", "block");
});
$('#close').bind("click", function (e) {
    $('#embedbox').css("display", "none");
});            