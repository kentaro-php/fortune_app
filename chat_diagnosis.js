// チャット診断のJavaScriptロジック

function startChat() {
    document.getElementById('chat-intro-screen').style.display = 'none';
    document.getElementById('chat-interface').style.display = 'block';
    
    // 最初のメッセージを表示
    setTimeout(() => {
        addBotMessage('こんにちは！占いミザリーです。\n彼の本気度を診断するために、いくつか質問させてください。');
        showTypingIndicator();
        
        setTimeout(() => {
            hideTypingIndicator();
            showOptions([
                'はい、お願いします',
                '少し不安ですが...'
            ]);
        }, 1500);
    }, 500);
}

function addBotMessage(text) {
    const timeline = document.getElementById('chat-timeline');
    const messageDiv = document.createElement('div');
    messageDiv.className = 'chat-message bot';
    messageDiv.textContent = text;
    timeline.appendChild(messageDiv);
    timeline.scrollTop = timeline.scrollHeight;
}

function addUserMessage(text) {
    const timeline = document.getElementById('chat-timeline');
    const messageDiv = document.createElement('div');
    messageDiv.className = 'chat-message user';
    messageDiv.textContent = text;
    timeline.appendChild(messageDiv);
    timeline.scrollTop = timeline.scrollHeight;
}

function showTypingIndicator() {
    document.getElementById('typing-indicator').classList.add('active');
}

function hideTypingIndicator() {
    document.getElementById('typing-indicator').classList.remove('active');
}

function showOptions(options) {
    const optionsArea = document.getElementById('chat-options-area');
    optionsArea.innerHTML = '';
    
    options.forEach((option, index) => {
        const button = document.createElement('button');
        button.className = 'option-btn';
        button.textContent = option;
        button.onclick = () => selectOption(option, index);
        optionsArea.appendChild(button);
    });
}

function selectOption(option, index) {
    addUserMessage(option);
    document.getElementById('chat-options-area').innerHTML = '';
    showTypingIndicator();
    
    // 診断ロジックを実装
    setTimeout(() => {
        hideTypingIndicator();
        // 次の質問や診断結果を表示
        processDiagnosis(option, index);
    }, 1000);
}

function processDiagnosis(option, index) {
    // 診断ロジックを実装
    // ここに質問フローと診断結果の計算を追加
    
    // 仮の診断結果表示
    setTimeout(() => {
        document.getElementById('chat-interface').style.display = 'none';
        document.getElementById('result-area').style.display = 'block';
        
        const resultDiv = document.getElementById('final-diagnosis-result');
        resultDiv.innerHTML = `
            <h4>診断結果</h4>
            <p>あなたへの本気度は...</p>
            <p style="font-size: 1.2rem; color: #e10080; font-weight: bold; margin-top: 10px;">
                中程度の本気度
            </p>
            <p style="margin-top: 15px;">
                彼の行動から判断すると、あなたへの関心はあるものの、まだ本気という段階には至っていない可能性があります。
                もう少し時間をかけて関係を深めていくことが大切です。
            </p>
        `;
    }, 2000);
}


