#requires -Version 5.1
# VelaLink for Windows - Persian hotspot control panel
Add-Type -AssemblyName PresentationFramework, PresentationCore, WindowsBase

function Require-Admin {
    $identity = [Security.Principal.WindowsIdentity]::GetCurrent()
    $principal = New-Object Security.Principal.WindowsPrincipal($identity)
    if (-not $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
        Start-Process powershell.exe -Verb RunAs -ArgumentList "-ExecutionPolicy Bypass -File `"$PSCommandPath`""
        exit
    }
}

function Set-InternetSharing($publicName, $privateName) {
    $share = New-Object -ComObject HNetCfg.HNetShare
    $public = $null; $private = $null
    foreach ($connection in $share.EnumEveryConnection) {
        $props = $share.NetConnectionProps($connection)
        if ($props.Name -eq $publicName) { $public = $connection }
        if ($props.Name -eq $privateName) { $private = $connection }
    }
    if (-not $public -or -not $private) { throw "اتصال اینترنت یا کارت هات‌اسپات پیدا نشد." }
    $publicConfig = $share.INetSharingConfigurationForINetConnection($public)
    $privateConfig = $share.INetSharingConfigurationForINetConnection($private)
    $publicConfig.EnableSharing(0)
    $privateConfig.EnableSharing(1)
}

Require-Admin

[xml]$xaml = @'
<Window xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation" xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml" Title="ولا لینک" Width="760" Height="620" WindowStartupLocation="CenterScreen" FlowDirection="RightToLeft" Background="#08101D" FontFamily="Segoe UI">
  <Window.Resources>
    <Style TargetType="Button"><Setter Property="Margin" Value="5"/><Setter Property="Padding" Value="16,9"/><Setter Property="Foreground" Value="#07150F"/><Setter Property="Background" Value="#39D2AE"/><Setter Property="BorderThickness" Value="0"/><Setter Property="FontWeight" Value="SemiBold"/><Setter Property="Cursor" Value="Hand"/></Style>
    <Style TargetType="TextBox"><Setter Property="Margin" Value="0,4,0,10"/><Setter Property="Padding" Value="10,8"/><Setter Property="Background" Value="#0D1727"/><Setter Property="Foreground" Value="#F3F7FF"/><Setter Property="BorderBrush" Value="#2A3C58"/><Setter Property="TextAlignment" Value="Right"/></Style>
    <Style TargetType="ComboBox"><Setter Property="Margin" Value="0,4,0,10"/><Setter Property="Padding" Value="8"/><Setter Property="Background" Value="#0D1727"/><Setter Property="Foreground" Value="#F3F7FF"/></Style>
  </Window.Resources>
  <Grid Margin="30"><Grid.RowDefinitions><RowDefinition Height="Auto"/><RowDefinition Height="Auto"/><RowDefinition Height="*"/><RowDefinition Height="Auto"/></Grid.RowDefinitions>
    <StackPanel Grid.Row="0"><TextBlock Text="ولا لینک" Foreground="#F3F7FF" FontSize="28" FontWeight="Bold"/><TextBlock Text="هات‌اسپات امن برای ویندوز" Foreground="#AAB8CB" FontSize="14" Margin="0,3,0,22"/></StackPanel>
    <Border Grid.Row="1" Background="#15233A" BorderBrush="#2A3C58" BorderThickness="1" CornerRadius="14" Padding="16" Margin="0,0,0,18"><StackPanel Orientation="Horizontal"><Ellipse x:Name="StateDot" Width="12" Height="12" Fill="#FF7186" Margin="0,2,10,0"/><StackPanel><TextBlock x:Name="StateText" Text="هات‌اسپات خاموش است" Foreground="#F3F7FF" FontSize="16" FontWeight="SemiBold"/><TextBlock Text="برای شروع، تنظیمات را وارد کن." Foreground="#AAB8CB" FontSize="12"/></StackPanel></StackPanel></Border>
    <Grid Grid.Row="2"><Grid.ColumnDefinitions><ColumnDefinition Width="*"/><ColumnDefinition Width="*"/></Grid.ColumnDefinitions>
      <StackPanel Grid.Column="0" Margin="0,0,8,0"><TextBlock Text="نام اتصال اینترنت" Foreground="#AAB8CB"/><ComboBox x:Name="Internet"/><TextBlock Text="نام کارت هات‌اسپات" Foreground="#AAB8CB"/><ComboBox x:Name="Hotspot"/><TextBlock Text="نام شبکهٔ Wi‑Fi" Foreground="#AAB8CB"/><TextBox x:Name="Ssid" Text="VelaLink"/><TextBlock Text="رمز Wi‑Fi (حداقل ۸ کاراکتر)" Foreground="#AAB8CB"/><PasswordBox x:Name="Password" Margin="0,4,0,10" Padding="10,8" Background="#0D1727" Foreground="#F3F7FF" BorderBrush="#2A3C58"/></StackPanel>
      <Border Grid.Column="1" Margin="8,0,0,0" Background="#101B2C" CornerRadius="14" Padding="18"><StackPanel><TextBlock Text="دربارهٔ نسخهٔ ویندوز" Foreground="#F3F7FF" FontSize="16" FontWeight="SemiBold"/><TextBlock TextWrapping="Wrap" Margin="0,12,0,0" Foreground="#AAB8CB" LineHeight="22" Text="این برنامه از ابزارهای داخلی ویندوز برای ساخت شبکه و اشتراک اینترنت استفاده می‌کند. برای پخش شبکه باید کارت Wi‑Fi از Hosted Network پشتیبانی کند."/><TextBlock TextWrapping="Wrap" Margin="0,14,0,0" Foreground="#F3C96E" LineHeight="22" Text="لایهٔ VLESS در نسخهٔ ویندوز هنوز فعال نشده است؛ برای جلوگیری از قطع‌شدن اینترنت ویندوز، به درایور شبکهٔ جداگانه نیاز دارد."/></StackPanel></Border>
    </Grid>
    <StackPanel Grid.Row="3" Orientation="Horizontal" HorizontalAlignment="Left" Margin="0,18,0,0"><Button x:Name="Stop" Content="خاموش کردن" Background="#422331" Foreground="#FFADBA"/><Button x:Name="Start" Content="روشن کردن هات‌اسپات"/><Button x:Name="Refresh" Content="بروزرسانی" Background="#7CA9FF" Foreground="#071226"/></StackPanel>
  </Grid>
</Window>
'@

$reader = New-Object System.Xml.XmlNodeReader $xaml
$window = [Windows.Markup.XamlReader]::Load($reader)
$internet = $window.FindName('Internet'); $hotspot = $window.FindName('Hotspot')
$ssid = $window.FindName('Ssid'); $password = $window.FindName('Password')
$state = $window.FindName('StateText'); $dot = $window.FindName('StateDot')

function Refresh-Adapters {
    $names = @(Get-NetAdapter -Physical | Where-Object Status -ne 'Disabled' | Select-Object -ExpandProperty Name)
    $internet.ItemsSource = $names; $hotspot.ItemsSource = $names
    if ($names.Count -gt 0) { $internet.SelectedIndex = 0; $hotspot.SelectedIndex = [Math]::Min(1, $names.Count - 1) }
}

$window.FindName('Refresh').Add_Click({ Refresh-Adapters })
$window.FindName('Start').Add_Click({
    try {
        if ($password.Password.Length -lt 8) { throw "رمز Wi‑Fi باید حداقل ۸ کاراکتر داشته باشد." }
        if ($internet.SelectedItem -eq $hotspot.SelectedItem) { throw "کارت اینترنت و کارت هات‌اسپات نباید یکی باشند." }
        & netsh wlan set hostednetwork mode=allow ssid=$ssid.Text key=$password.Password | Out-Null
        & netsh wlan start hostednetwork | Out-Null
        Set-InternetSharing $internet.SelectedItem $hotspot.SelectedItem
        $state.Text = "هات‌اسپات روشن است"; $dot.Fill = '#39D2AE'
        [System.Windows.MessageBox]::Show('هات‌اسپات روشن شد.','ولا لینک')
    } catch { [System.Windows.MessageBox]::Show($_.Exception.Message,'ولا لینک') }
})
$window.FindName('Stop').Add_Click({
    & netsh wlan stop hostednetwork | Out-Null
    $state.Text = "هات‌اسپات خاموش است"; $dot.Fill = '#FF7186'
})
Refresh-Adapters
$window.ShowDialog() | Out-Null
