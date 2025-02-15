# Define o diretório onde estão as pastas (ou use "." para a pasta atual)
$directory = "."

# Obtém todas as pastas dentro do diretório
$folders = Get-ChildItem -Path $directory -Directory

foreach ($folder in $folders) {
    # Remove "genesis" e capitaliza cada palavra
    $newName = ($folder.Name -replace "\bgenesis\b", "") -split ' ' | ForEach-Object { $_.Substring(0,1).ToUpper() + $_.Substring(1) }

    # Junta as palavras de volta em uma string com espaços
    $newName = $newName -join ' '

    # Remove espaços extras no início ou no fim
    $newName = $newName.Trim()

    # Se o nome mudou, renomeia a pasta
    if ($folder.Name -ne $newName) {
        Write-Output "Renomeando '$($folder.Name)' para '$newName'"
        Rename-Item -Path $folder.FullName -NewName $newName
    }
}

Write-Output "Renomeação concluída!"
