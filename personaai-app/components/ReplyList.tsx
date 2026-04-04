import { View } from "react-native";

import { ReplyCard } from "@/components/ReplyCard";

type Reply = {
  id: string;
  rank: number;
  text: string;
};

type ReplyListProps = {
  replies: Reply[];
};

export function ReplyList({ replies }: ReplyListProps) {
  return (
    <View style={{ gap: 12 }}>
      {replies.map((reply) => (
        <ReplyCard key={reply.id} rank={reply.rank} text={reply.text} />
      ))}
    </View>
  );
}
