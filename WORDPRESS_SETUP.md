# WordPressフローティングボタン設置ガイド

## 設置手順

### ステップ1: CSSの追加

1. WordPress管理画面にログイン
2. **外観** → **カスタマイズ** をクリック
3. **追加CSS** をクリック
4. `wordpress_floating_button.css` の内容をすべてコピー＆ペースト
5. **公開** をクリック

### ステップ2: HTMLの追加

1. **外観** → **ウィジェット** をクリック
2. **フッター** または適切なウィジェットエリアを選択
3. **カスタムHTML** ウィジェットを追加
4. `wordpress_floating_button.html` の内容をコピー＆ペースト
5. **`YOUR_STRIPE_URL_HERE`** の部分を実際のStripe決済ページのURLに置き換え
6. **保存** をクリック

## カスタマイズ方法

### 位置の調整

CSSファイル内の以下の値を変更してください：

```css
#fortune-floating-button {
  right: 20px;    /* 右端からの距離 */
  bottom: 100px;  /* 下からの距離（チャットボタンとの間隔） */
}
```

### アイコンモードに切り替え

HTMLファイル内の `#fortune-floating-button` に `icon-mode` クラスを追加すると、テキストの代わりにキラキラアイコンが表示されます：

```html
<div id="fortune-floating-button" class="icon-mode">
```

### 色の調整

グラデーションの色を変更したい場合は、CSSファイル内の以下を編集：

```css
background: linear-gradient(135deg, #C5A059 0%, #E8B4B8 50%, #FFB6C1 100%);
```

- `#C5A059`: ゴールド色
- `#E8B4B8`: 中間色（ピンク）
- `#FFB6C1`: ライトピンク

### アニメーション速度の調整

アニメーションの間隔を変更する場合：

```css
#fortune-floating-button {
  animation: bounce 3s infinite; /* 3秒を変更 */
}
```

## 注意事項

- チャットボタンの位置に応じて `bottom` の値を調整してください
- モバイル表示でも適切に表示されるよう、レスポンシブ対応済みです
- z-indexは9999に設定しているため、ほとんどの要素の上に表示されます





