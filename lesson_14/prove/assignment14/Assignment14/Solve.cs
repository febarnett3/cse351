using System.Collections.Concurrent;
using Newtonsoft.Json.Linq;

namespace Assignment14;

public static class Solve
{
    private static readonly HttpClient HttpClient = new()
    {
        Timeout = TimeSpan.FromSeconds(180)
    };
    public const string TopApiUrl = "http://127.0.0.1:8123";

    // This function retrieves JSON from the server
    public static async Task<JObject?> GetDataFromServerAsync(string url)
    {
        try
        {
            var jsonString = await HttpClient.GetStringAsync(url);
            return JObject.Parse(jsonString);
        }
        catch (HttpRequestException e)
        {
            Console.WriteLine($"Error fetching data from {url}: {e.Message}");
            return null;
        }
    }

    // This function takes in a person ID and retrieves a Person object
    // Hint: It can be used in a "new List<Task<Person?>>()" list
    private static async Task<Person?> FetchPersonAsync(long personId)
    {
        var personJson = await Solve.GetDataFromServerAsync($"{Solve.TopApiUrl}/person/{personId}");
        return personJson != null ? Person.FromJson(personJson.ToString()) : null;
    }

    // This function takes in a family ID and retrieves a Family object
    // Hint: It can be used in a "new List<Task<Family?>>()" list
    private static async Task<Family?> FetchFamilyAsync(long familyId)
    {
        var familyJson = await Solve.GetDataFromServerAsync($"{Solve.TopApiUrl}/family/{familyId}");
        return familyJson != null ? Family.FromJson(familyJson.ToString()) : null;
    }
    
    // =======================================================================================================
    public static async Task<bool> DepthFS(long familyId, Tree tree)
    {
        // Base case — skip if invalid or already processed
        if (familyId == 0 || tree.GetFamily(familyId) != null)
            return false;

        // Fetch the family from the server
        Family? family = await FetchFamilyAsync(familyId);
        if (family == null)
            return false;

        // Add the family to the tree
        tree.AddFamily(family);

        // Fetch husband, wife, and children in parallel
        var personTasks = new List<Task<Person?>>
        {
            FetchPersonAsync(family.HusbandId),
            FetchPersonAsync(family.WifeId)
        };
        personTasks.AddRange(family.Children.Select(FetchPersonAsync));
    
        var people = await Task.WhenAll(personTasks);

        // Add people to the tree (thread-safe check)
        foreach (var person in people)
        {
            if (person != null && !tree.PersonExists(person.Id))
            {
                tree.AddPerson(person);
            }
        }

        // Create parallel recursion tasks for parent families
        var recursionTasks = new List<Task>();

        foreach (var person in people)
        {
            if (person != null && person.ParentId != 0 && tree.GetFamily(person.ParentId) == null)
            {
                recursionTasks.Add(DepthFS(person.ParentId, tree));
            }
        }

        // Wait for all recursive calls to finish
        await Task.WhenAll(recursionTasks);

        return true;
    }


    // =======================================================================================================
    public static async Task<bool> BreathFS(long famid, Tree tree)
{
    if (famid == 0) return false;

    var visited = new ConcurrentDictionary<long, byte>();
    var queue = new ConcurrentQueue<long>();
    var allTasks = new List<Task>();

    queue.Enqueue(famid);

    // Keep looping while there's work to do
    while (!queue.IsEmpty || allTasks.Any(t => !t.IsCompleted))
    {
        // While there are families in the queue
        while (queue.TryDequeue(out long currentFamId))
        {
            // Avoid revisiting the same family
            if (!visited.TryAdd(currentFamId, 0))
                continue;

            var task = Task.Run(async () =>
            {
                var family = await FetchFamilyAsync(currentFamId);
                if (family == null) return;

                tree.AddFamily(family);

                // Fetch people concurrently
                var personTasks = new List<Task<Person?>>
                {
                    FetchPersonAsync(family.HusbandId),
                    FetchPersonAsync(family.WifeId)
                };
                personTasks.AddRange(family.Children.Select(FetchPersonAsync));
                var people = await Task.WhenAll(personTasks);

                foreach (var person in people)
                {
                    if (person != null && !tree.PersonExists(person.Id))
                        tree.AddPerson(person);
                }

                // Enqueue parents of people for future processing
                foreach (var person in people)
                {
                    if (person != null && person.ParentId != 0 && !visited.ContainsKey(person.ParentId))
                    {
                        queue.Enqueue(person.ParentId);
                    }
                }
            });

            allTasks.Add(task);
        }

        // Wait briefly to allow queue to refill if tasks are still running
        await Task.Delay(10);
    }

    // Make sure all tasks finish
    await Task.WhenAll(allTasks);
    return true;
}


}