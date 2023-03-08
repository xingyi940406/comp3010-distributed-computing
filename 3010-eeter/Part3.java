import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.OutputStream;
import java.net.Socket;
import java.net.UnknownHostException;
import java.nio.charset.StandardCharsets;
import java.util.HashMap;
import java.util.Map;
import java.util.function.Consumer;

public class Part3 {
    
    public static void main(String[] args) throws IOException {
        String id = post();
        delete(id, "admin", result -> {
            System.out.println(isUnauthorized(result) 
                ? "Assertion PASSED for failing to delete post" 
                : "Assertion FAILED for failing to delete post");
        });
        delete(id, "david", result -> {
            System.out.println(isOk(result) 
                ? "Assertion PASSED for deleting post" 
                : "Assertion FAILED for deleting post");
        });
    }

    private static void delete(String id, String user, Consumer<String> assertion) throws UnknownHostException, IOException {
        System.out.println("Deleting a post as " + user);
        String serverAddress = "localhost";
        int serverPort = 3000;
        Socket socket = new Socket(serverAddress, serverPort);
        
        String path = "/api/tweet/" + id;
        String cookie = "Cookie: user=" + user;        
        String request = "DELETE " + path + " HTTP/1.1\r\n" +
            "Host: " + serverAddress + ":" + serverPort + "\r\n" +
            "Content-Type: application/json\r\n" +
            cookie + "\r\n" +
            "Origin: null\r\n" +
            "Connection: close\r\n\r\n";
        
        OutputStream outputStream = socket.getOutputStream();
        outputStream.write(request.getBytes(StandardCharsets.UTF_8));
        outputStream.flush();
        
        BufferedReader reader = new BufferedReader(new InputStreamReader(socket.getInputStream()));
        String line;
        Map<String, String> result = new HashMap<>();
        while ((line = reader.readLine()) != null) {
            String key = line.split(" ")[0];
            result.put(key, line);
        }

        assertion.accept(result.get("HTTP/1.1"));

        socket.close();
    }

    private static boolean isUnauthorized(String result) {
        return result.contains("Unauthorized");
    }

    private static boolean isOk(String result) {
        return result.contains("OK");
    }

    private static String post() throws UnknownHostException, IOException {
        System.out.println("Adding a post as david");
        String serverAddress = "localhost";
        int serverPort = 3000;
        Socket socket = new Socket(serverAddress, serverPort);
        
        String path = "/api/tweet";
        String cookie = "Cookie: user=david";
        String body = "{\"content\": \"Hello world!\", \"author\": \"david\"}"; // Replace with your post data
        
        String request = "POST " + path + " HTTP/1.1\r\n" +
                         "Host: " + serverAddress + ":" + serverPort + "\r\n" +
                         "Content-Type: application/json\r\n" +
                         "Content-Length: " + body.length() + "\r\n" +
                         cookie + "\r\n" +
                         "Origin: null\r\n" +
                         "Connection: close\r\n\r\n" +
                         body;
        
        OutputStream outputStream = socket.getOutputStream();
        outputStream.write(request.getBytes(StandardCharsets.UTF_8));
        outputStream.flush();
        
        BufferedReader reader = new BufferedReader(new InputStreamReader(socket.getInputStream()));
        String line, result = null;
        while ((line = reader.readLine()) != null) {
            result = line;
        }

        String id = result.split(", ")[0].split(": ")[1];
        System.out.println("New post ID " + id);
        socket.close();
        return id;
    }
}
