/*
* PWA Install Logic
*/

let deferredPrompt;

// Detect iOS
const isIos = () => {
  const userAgent = window.navigator.userAgent.toLowerCase();
  return /iphone|ipad|ipod/.test(userAgent);
};

// Check if launched as PWA
const isInStandalone = () => {
    return (window.matchMedia('(display-mode: standalone)').matches) || (window.navigator.standalone === true);
};

if (!isInStandalone()) {
    // Android / Desktop
    window.addEventListener('beforeinstallprompt', (e) => {
        // Prevent the mini-infobar from appearing on mobile
        e.preventDefault();
        // Stash the event so it can be triggered later.
        deferredPrompt = e;
        // Update UI notify the user they can install the PWA
        showInstallPromotion();
    });

    // iOS check
    // Wait a bit to not be aggressive
    setTimeout(() => {
        if (isIos()) {
            showIosInstallInstruction();
        }
    }, 2000);
}

function showInstallPromotion() {
    // Add install button/modal if not present
    const existingModal = document.getElementById('pwa-install-modal');
    if(existingModal) {
        existingModal.classList.remove('hidden');
    } else {
        createInstallModal();
    }
}

function showIosInstallInstruction() {
    // Show iOS specific modal
    if(localStorage.getItem('pwa-ios-dismissed')) return;

    const existingModal = document.getElementById('pwa-ios-modal');
    if(existingModal) {
        existingModal.classList.remove('hidden');
    } else {
        createIosModal();
    }
}

function createInstallModal() {
    const div = document.createElement('div');
    div.id = 'pwa-install-modal';
    div.className = 'fixed bottom-4 right-4 z-50 bg-white p-4 rounded-xl shadow-lg border border-indigo-100 flex items-center gap-4 animate-bounce-in transition-all duration-300 transform translate-y-0';
    div.style.maxWidth = '300px';
    div.innerHTML = `
        <div class="flex-1">
            <h3 class="font-bold text-gray-800 text-sm">Installer l'Application</h3>
            <p class="text-xs text-gray-500">Accédez plus rapidement à vos données.</p>
        </div>
        <button id="pwa-install-action" class="px-3 py-1.5 bg-indigo-600 text-white text-xs font-bold rounded-lg hover:bg-indigo-700 transition-colors">
            Installer
        </button>
        <button onclick="document.getElementById('pwa-install-modal').remove()" class="text-gray-400 hover:text-gray-600 ml-2">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path></svg>
        </button>
    `;
    document.body.appendChild(div);

    document.getElementById('pwa-install-action').addEventListener('click', async () => {
        if (deferredPrompt) {
            deferredPrompt.prompt();
            const { outcome } = await deferredPrompt.userChoice;
            console.log(`User response to the install prompt: ${outcome}`);
            deferredPrompt = null;
            document.getElementById('pwa-install-modal').remove();
        }
    });
}

function createIosModal() {
    const div = document.createElement('div');
    div.id = 'pwa-ios-modal';
    div.className = 'fixed bottom-0 left-0 right-0 z-50 bg-white/95 backdrop-blur-sm p-6 rounded-t-2xl shadow-[0_-4px_6px_-1px_rgba(0,0,0,0.1)] border-t border-gray-100 transition-all duration-300 transform translate-y-0';
    div.innerHTML = `
        <div class="flex items-start gap-4 max-w-lg mx-auto">
            <div class="bg-gray-100 p-2 rounded-xl hidden sm:block">
                <svg class="w-8 h-8 text-indigo-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 18h.01M8 21h8a2 2 0 002-2V5a2 2 0 00-2-2H8a2 2 0 00-2 2v14a2 2 0 002 2z"></path></svg>
            </div>
            <div class="flex-1">
                <h3 class="font-bold text-gray-800 mb-1">Installer sur iPhone / iPad</h3>
                <p class="text-sm text-gray-600 mb-3">Pour installer l'application :</p>
                <ol class="list-decimal list-inside text-sm text-gray-600 space-y-2">
                    <li>Appuyez sur le bouton <strong>Partager</strong> <svg class="w-5 h-5 inline text-blue-500 mx-1" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8.684 13.342C8.886 12.938 9 12.482 9 12c0-.482-.114-.938-.316-1.342m0 2.684a3 3 0 110-2.684m0 2.684l6.632 3.316m-6.632-6l6.632-3.316m0 0a3 3 0 105.367-2.684 3 3 0 00-5.367 2.684zm0 9.316a3 3 0 105.368 2.684 3 3 0 00-5.368-2.684z"></path></svg></li>
                    <li>Sélectionnez <strong>Sur l'écran d'accueil</strong> <svg class="w-5 h-5 inline text-gray-800 mx-1" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v3m0 0v3m0-3h3m-3 0H9m12 0a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg></li>
                </ol>
            </div>
            <button onclick="dismissIosModal()" class="text-gray-400 hover:text-gray-600 p-1 absolute top-4 right-4">
                <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path></svg>
            </button>
        </div>
    `;
    document.body.appendChild(div);
}

function dismissIosModal() {
    const modal = document.getElementById('pwa-ios-modal');
    if (modal) modal.remove();
    localStorage.setItem('pwa-ios-dismissed', 'true');
}
