// Sipay 3D Secure Simülasyon Sayfası - Otomatik "Yes" Butonu
// Bu kodu Sipay'in 3D Secure simülasyon sayfasında F12 > Console'da çalıştırın

(function() {
    console.log('🎯 Sipay 3D Secure simülasyon sayfasında otomatik "Yes" butonu aranıyor...');
    
    // "Yes" butonunu bul
    function findAndClickYes() {
        const selectors = [
            'button[name="result"][value="y"]',
            '#yes',
            '.button[value="y"]',
            'input[name="result"][value="y"]',
            'button:contains("Yes")',
            'input[value="y"]'
        ];
        
        for (let selector of selectors) {
            const button = document.querySelector(selector);
            if (button) {
                console.log('✅ "Yes" butonu bulundu:', button);
                console.log('🔄 1 saniye sonra otomatik tıklanacak...');
                
                setTimeout(() => {
                    button.click();
                    console.log('✅ "Yes" butonuna tıklandı!');
                }, 1000);
                
                return true;
            }
        }
        
        // Text içeriğine göre ara
        const allButtons = document.querySelectorAll('button, input[type="submit"], input[type="button"]');
        for (let button of allButtons) {
            if (button.textContent.toLowerCase().includes('yes') || 
                button.value === 'y' || 
                button.value === 'yes') {
                console.log('✅ "Yes" butonu bulundu (text içeriği ile):', button);
                console.log('🔄 1 saniye sonra otomatik tıklanacak...');
                
                setTimeout(() => {
                    button.click();
                    console.log('✅ "Yes" butonuna tıklandı!');
                }, 1000);
                
                return true;
            }
        }
        
        return false;
    }
    
    // İlk deneme
    if (!findAndClickYes()) {
        console.log('⚠️ "Yes" butonu bulunamadı, 2 saniye sonra tekrar denenecek...');
        
        // 2 saniye sonra tekrar dene
        setTimeout(() => {
            if (!findAndClickYes()) {
                console.log('❌ "Yes" butonu bulunamadı. Sayfayı yenileyip tekrar deneyin.');
            }
        }, 2000);
    }
    
    // DOM değişikliklerini izle
    const observer = new MutationObserver(function(mutations) {
        mutations.forEach(function(mutation) {
            if (mutation.type === 'childList') {
                findAndClickYes();
            }
        });
    });
    
    observer.observe(document.body, {
        childList: true,
        subtree: true
    });
    
    console.log('👀 DOM değişiklikleri izleniyor...');
})();
