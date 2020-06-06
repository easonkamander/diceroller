mdc.autoInit();

drawerOpen = true;
document.querySelector('.mdc-drawer').MDCDrawer.open = drawerOpen;
document.querySelector('.mdc-drawer-app-content').style.marginLeft = drawerOpen ? '300px' : '0';

document.querySelector('.mdc-top-app-bar__navigation-icon').addEventListener('click', () => {
	drawerOpen = !drawerOpen;
	document.querySelector('.mdc-drawer').style.left = drawerOpen ? '0' : '-300px';
	document.querySelector('.mdc-drawer-app-content').style.marginLeft = drawerOpen ? '300px' : '0';
});

let socket;
const socketPng = 2;
const socketMax = 3;
let socketTmtWrn = null;
let socketTmtErr = null;
let userkey;

const receive = (msg) => {
	if ('order' in msg && msg['order'] == 'group') {
		if ('list' in msg) {
			document.querySelector('#membersList').innerHTML = '';
			for (let member of msg['list']) {
				let item = document.createElement('li');
				item.classList.add('mdc-list-item');
				let span = document.createElement('span');
				span.classList.add('mdc-list-item__text');
				span.innerHTML = member[0];
				item.appendChild(span);
				let icon = document.createElement('i');
				icon.classList.add('material-icons');
				icon.classList.add('mdc-top-app-bar__navigation-icon');
				icon.classList.add(member[1] == 0 ? 'networkFull' : (member[1] == 1 ? 'networkHalf' : 'networkNone'));
				icon.innerHTML = member[1] == 0 ? 'wifi' : (member[1] == 1 ? 'network_check' : 'wifi_off');
				item.appendChild(icon);
				document.querySelector('#membersList').appendChild(item);
			}
		}
		if ('name' in msg) {
			document.querySelector('#groupName').MDCTextField.value = msg['name'] ? msg['name'] : '';
		}
		if ('crt' in msg) {
			document.querySelector('.mdc-drawer').style.width = '300px';
			document.querySelector('#name').style.margin = '0';
			document.querySelector('#groupCodeDialogTitleContent').innerHTML = msg['crt'];
			document.querySelector('#groupCodeDialogCopy').setAttribute('value', msg['crt']);
			document.querySelector('#groupCodeDialog').MDCDialog.open();
			document.querySelector('#groupSelect').style.display = 'none';
			document.querySelector('#groupName').style.display = 'inline-flex';
			document.querySelector('#membersOuter').style.display = 'initial';
		}
		if ('att' in msg) {
			if (msg['att']) {
				document.querySelector('.mdc-drawer').style.width = '300px';
				document.querySelector('#name').style.margin = '0';
				document.querySelector('#groupCode').style.display = 'none';
				document.querySelector('#groupName').style.display = 'inline-flex';
				document.querySelector('#membersOuter').style.display = 'initial';
			} else {
				document.querySelector('#groupCode').style.display = 'none';
				document.querySelector('#groupSelect').MDCSelect.value = 'none';
				document.querySelector('#groupSelect').style.display = 'inline-flex';
			}
		}
		if ('rmv' in msg) {
			document.querySelector('.mdc-drawer').style.width = '100%';
			document.querySelector('#name').style.margin = '0 1rem';
			document.querySelector('#groupName').style.display = 'none';
			document.querySelector('#membersOuter').style.display = 'none';
			document.querySelector('#groupSelect').MDCSelect.value = 'none';
			document.querySelector('#groupSelect').style.display = 'inline-flex';
		}
		if ('qry' in msg) {
			let elemQueryUser = document.createElement('div');
			elemQueryUser.innerHTML = msg['qry']['name'];
			document.querySelector('#results').insertBefore(elemQueryUser, document.querySelector('#results #insert').nextSibling);
			let elemQueryRes = document.createElement('div');
			elemQueryRes.innerHTML = msg['qry']['res'];
			document.querySelector('#results').insertBefore(elemQueryRes, elemQueryUser.nextSibling);
			let elemQueryRaw = document.createElement('div');
			elemQueryRaw.innerHTML = msg['qry']['req'];
			document.querySelector('#results').insertBefore(elemQueryRaw, elemQueryRes.nextSibling);	
		}
	} else {
		if ('key' in msg) {
			userkey = msg['key'];
		}
		if ('name' in msg) {
			document.querySelector('#name').MDCTextField.value = msg['name'];
		}
		if ('ping' in msg) {
			send({'ping': true});
			clearTimeout(socketTmtWrn);
			clearTimeout(socketTmtErr);
			socketTmtWrn = setTimeout(() => {
				document.querySelector('#networkFull').style.display = 'none';
				document.querySelector('#networkHalf').style.display = 'inline-block';
				document.querySelector('#networkNone').style.display = 'none';
			}, socketPng*1000);
			socketTmtErr = setTimeout(() => {
				document.querySelector('#networkFull').style.display = 'none';
				document.querySelector('#networkHalf').style.display = 'none';
				document.querySelector('#networkNone').style.display = 'inline-block';
			}, socketPng*socketMax*1000);
		}
	}
};

const send = msg => {
	socket.send(JSON.stringify(msg));
};

const initSocket = () => {
	console.log(userkey);
	console.log('wss://misc.easonkamander.com/diceroller/ws' + (userkey ? '?user='+userkey : ''));
	socket = new WebSocket('wss://misc.easonkamander.com/diceroller/ws' + (userkey ? '?user='+userkey : ''));
	socket.addEventListener('open', () => {
		document.querySelector('#networkFull').style.display = 'inline-block';
		document.querySelector('#networkHalf').style.display = 'none';
		document.querySelector('#networkNone').style.display = 'none';
	});
	socket.addEventListener('message', (e) => {
		console.log(e.data);
		receive(JSON.parse(e.data));
		document.querySelector('#networkFull').style.display = 'inline-block';
		document.querySelector('#networkHalf').style.display = 'none';
		document.querySelector('#networkNone').style.display = 'none';
	});
	socket.addEventListener('close', (e) => {
		console.log(e);
		initSocket();
	});
}

Array.from(document.querySelectorAll('.configOuter')).map(configOuter => {
	let configInput = configOuter.querySelector('.configInput');
	let configSubmit = configOuter.querySelector('.configSubmit');

	let actionSubmit = () => {
		let msg = {'order': configOuter.dataset.sendOrder};
		msg[configOuter.dataset.sendName] = configOuter.MDCTextField.value;
		if (configSubmit != document.querySelector('#qryAlwaysOnButton')) {
			configOuter.MDCTextField.value = '';
			configInput.blur();
		}
		send(msg);
	};

	configInput.addEventListener('focus', () => {
		configSubmit.style.display = 'inline-block';
	});

	configInput.addEventListener('focusout', (e) => {
		if (e.relatedTarget != configSubmit) {
			configSubmit.style.display = 'none';
			// red line
		}
	});

	configInput.addEventListener('keyup', (e) => {
    	if (e.key == 'Enter') {
			actionSubmit();
		}
	});

	configSubmit.addEventListener('click', () => {
		actionSubmit();
	});
});

document.querySelector('#groupSelect').MDCSelect.listen('MDCSelect:change', () => {
	if (document.querySelector('#groupSelect').MDCSelect.value == 'crt') {
		send({'order': 'group', 'crt': true});
	} else if (document.querySelector('#groupSelect').MDCSelect.value == 'att') {
		document.querySelector('#groupSelect').style.display = 'none';
		document.querySelector('#groupCode').style.display = 'inline-flex';
		document.querySelector('#groupCode').MDCTextField.focus();
	}
});

document.querySelector('#groupName .configQuit').addEventListener('click', () => {
	document.querySelector('#groupQuitDialog').MDCDialog.open();
});

document.querySelector('#groupQuitDialog').MDCDialog.listen('MDCDialog:closed', (e) => {
	if (e.detail.action == 'yes') {
		send({'order': 'group', 'rmv': true});
	}
});

document.querySelector('#groupCodeDialog').MDCDialog.listen('MDCDialog:closing', (e) => {
	if (e.detail.action == 'copy') {
		document.querySelector('#groupCodeDialogCopy').select();
		document.execCommand('copy');
	}
});

document.querySelector('#groupName .configInput').addEventListener('focus', () => {
	document.querySelector('#groupName .configQuit').style.display = 'none';
});

document.querySelector('#groupName .configInput').addEventListener('focusout', () => {
	document.querySelector('#groupName .configQuit').style.display = 'inline-block';
});

initSocket();