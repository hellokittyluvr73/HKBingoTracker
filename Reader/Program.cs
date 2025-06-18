using System;
using System.Threading.Tasks;
using BingoSyncAPI; // Core API
using static BingoSyncAPI.BingoSync;
using static BingoSyncAPI.BingoSyncTypes;
public class Program
{
  public static async Task Main(string[] args)
  {
    BingoGame game = new BingoGame();
    game.Init();
    await game.JoinBingoSyncRoom();
    string path = @"C://Bingo//match.txt";
    string now = DateTime.Now.ToString("hh:mm:ss");
    File.WriteAllText(path, now + Environment.NewLine);
    Console.WriteLine("Press enter to close program");
    Console.ReadLine();
  }
 
}
public class BingoGame
{
  private readonly BingoSync bingoSync = new BingoSync();

 public void Init()
  {
    bingoSync.OnMessageReceived += OnRoomEvent;
  }


  public async Task JoinBingoSyncRoom()
  {

    Console.WriteLine("Enter Room ID");
    string ID = Console.ReadLine();
    Console.WriteLine("Enter Room Password");
    string password = Console.ReadLine();


    var myRoomInfo = new RoomInfo
    (
        ID,   // Room ID
        password,                    // Password
        "The Watcher Knight",                     // Name
        PlayerColors.Pink,          // Color
        false                      // Spectator
    );

    if (await bingoSync.JoinRoom(myRoomInfo) == BingoSync.ConnectionStatus.Connected)
    {
      Console.WriteLine("Successfully connected to room!");

      await bingoSync.SendChatMessage("Bingy!");
    }
    else
    {
      Console.WriteLine("Failed to connect.");
    }

    
  }
  private void OnRoomEvent(SocketMessage message)
  {

    string chatMessage = string.Empty;
    int changedSquareOnBoard = 1;
    string playerWhoMarked = string.Empty;
    string goalMarked = string.Empty;
    switch (message.type) // connection, goal, revealed, color, chat, new-card
    {
      case "chat":
        chatMessage = message.text;
        Console.WriteLine(chatMessage);
        break;
      case "goal":
        if (int.TryParse(message.square.slot.Replace("slot", ""), out int result))
          changedSquareOnBoard = result;
        playerWhoMarked = message.player.name;
        goalMarked = message.square.name;
        string path = @"C://Bingo//match.txt";
        string now = DateTime.Now.ToString("hh:mm:ss");
        if (!File.Exists(path))
        {
          string createText = now + "," + playerWhoMarked + "," + goalMarked + "," + changedSquareOnBoard + Environment.NewLine;
          File.WriteAllText(path, createText);
        }
        else
        {
          string createText = now + "," + playerWhoMarked + "," + goalMarked + "," + changedSquareOnBoard + Environment.NewLine;
          File.AppendAllText(path, createText);
        }
        
        //Console.WriteLine($"{now}, {playerWhoMarked}, {goalMarked}");

        break;


    }
  }
}




















  
